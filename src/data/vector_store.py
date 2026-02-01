"""ChromaDB vector store client with connection pooling and CRUD operations."""

import logging
import time
from collections.abc import Generator
from contextlib import contextmanager
from threading import Lock
from typing import Any

import chromadb
from chromadb.api import ClientAPI
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .config import ChromaDBSettings, get_chroma_settings
from .exceptions import (
    CollectionError,
    ConnectionError,
    EmbeddingError,
    QueryError,
    ValidationError,
)
from .models import CollectionInfo, Document, HealthStatus, QueryRequest, QueryResult

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Simple connection pool for ChromaDB clients."""

    def __init__(self, settings: ChromaDBSettings):
        """
        Initialize connection pool.

        Args:
            settings: ChromaDB configuration settings
        """
        self.settings = settings
        self._pool: list[ClientAPI] = []
        self._lock = Lock()
        self._max_connections = settings.max_connections
        self._active_connections = 0

    def _create_client(self) -> ClientAPI:
        """
        Create a new ChromaDB client.

        Returns:
            ClientAPI: New ChromaDB client instance

        Raises:
            ConnectionError: If client creation fails
        """
        try:
            logger.info(f"Creating ChromaDB client for {self.settings.connection_url}")

            # Configure settings for HTTP client
            chroma_settings = Settings(
                chroma_api_impl="chromadb.api.fastapi.FastAPI",
                chroma_server_host=self.settings.host,
                chroma_server_http_port=self.settings.port,
            )

            # Build client kwargs
            client_kwargs = {
                "host": self.settings.host,
                "port": self.settings.port,
                "settings": chroma_settings,
            }

            # Add authentication if configured
            if self.settings.auth_credentials:
                username, password = self.settings.auth_credentials.split(":", 1)
                client_kwargs["headers"] = {
                    "Authorization": f"Basic {__import__('base64').b64encode(f'{username}:{password}'.encode()).decode()}"
                }

            client = chromadb.HttpClient(**client_kwargs)

            logger.info("ChromaDB client created successfully")
            return client

        except Exception as e:
            logger.error(f"Failed to create ChromaDB client: {e}")
            raise ConnectionError(f"Failed to create ChromaDB client: {e}")

    @contextmanager
    def get_client(self) -> Generator[ClientAPI, None, None]:
        """
        Get a client from the pool (context manager).

        Yields:
            ClientAPI: ChromaDB client instance
        """
        client = None
        try:
            with self._lock:
                if self._pool:
                    client = self._pool.pop()
                    logger.debug("Reusing client from pool")
                elif self._active_connections < self._max_connections:
                    client = self._create_client()
                    self._active_connections += 1
                    logger.debug(f"Created new client (active: {self._active_connections})")
                else:
                    # Wait for available connection
                    logger.warning("Connection pool exhausted, waiting...")

            # If no client available, create temporary one
            if client is None:
                client = self._create_client()

            yield client

        finally:
            # Return client to pool
            if client is not None:
                with self._lock:
                    if len(self._pool) < self._max_connections:
                        self._pool.append(client)
                        logger.debug("Returned client to pool")

    def close_all(self):
        """Close all connections in the pool."""
        with self._lock:
            self._pool.clear()
            self._active_connections = 0
            logger.info("Closed all connections in pool")


class VectorStore:
    """
    ChromaDB vector store client with full CRUD operations.

    This class provides a high-level interface for interacting with ChromaDB,
    including connection pooling, error handling, retry logic, and comprehensive
    logging.
    """

    def __init__(
        self,
        settings: ChromaDBSettings | None = None,
        embedding_model: SentenceTransformer | None = None,
    ):
        """
        Initialize vector store client.

        Args:
            settings: ChromaDB configuration settings
            embedding_model: Pre-loaded embedding model (optional)
        """
        self.settings = settings or get_chroma_settings()
        self._pool = ConnectionPool(self.settings)
        self._embedding_model = embedding_model
        self._embedding_model_name = self.settings.embedding_function

        logger.info(f"VectorStore initialized with collection: {self.settings.collection_name}")

    @property
    def embedding_model(self) -> SentenceTransformer:
        """
        Lazy-load embedding model.

        Returns:
            SentenceTransformer: Embedding model instance
        """
        if self._embedding_model is None:
            logger.info(f"Loading embedding model: {self._embedding_model_name}")
            self._embedding_model = SentenceTransformer(self._embedding_model_name)
        return self._embedding_model

    def _generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for texts.

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors

        Raises:
            EmbeddingError: If embedding generation fails
        """
        try:
            logger.debug(f"Generating embeddings for {len(texts)} texts")
            embeddings = self.embedding_model.encode(texts, show_progress_bar=False).tolist()
            logger.debug(f"Generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise EmbeddingError(f"Failed to generate embeddings: {e}")

    @retry(
        retry=retry_if_exception_type((ConnectionError, chromadb.errors.ChromaError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def _get_or_create_collection(self, client: ClientAPI, collection_name: str | None = None):
        """
        Get or create a collection with retry logic.

        Args:
            client: ChromaDB client
            collection_name: Collection name (uses default if not provided)

        Returns:
            Collection instance

        Raises:
            CollectionError: If collection operation fails
        """
        name = collection_name or self.settings.collection_name
        try:
            logger.debug(f"Getting or creating collection: {name}")
            collection = client.get_or_create_collection(
                name=name,
                metadata={"description": "Credit risk document embeddings"},
            )
            logger.info(f"Collection '{name}' ready (count: {collection.count()})")
            return collection
        except Exception as e:
            logger.error(f"Collection operation failed: {e}")
            raise CollectionError(f"Failed to get/create collection '{name}': {e}")

    def add_documents(
        self,
        documents: list[Document],
        collection_name: str | None = None,
        batch_size: int | None = None,
    ) -> dict[str, Any]:
        """
        Add documents to the vector store.

        Args:
            documents: List of documents to add
            collection_name: Target collection name
            batch_size: Batch size for processing

        Returns:
            Dict with operation results

        Raises:
            ValidationError: If documents are invalid
            EmbeddingError: If embedding generation fails
            CollectionError: If adding documents fails
        """
        if not documents:
            raise ValidationError("Documents list cannot be empty")

        batch_size = batch_size or self.settings.batch_size
        logger.info(f"Adding {len(documents)} documents in batches of {batch_size}")

        try:
            # Extract data
            ids = [doc.id for doc in documents]
            contents = [doc.content for doc in documents]
            metadatas = [doc.metadata for doc in documents]

            # Generate embeddings if not provided
            embeddings = []
            for doc in documents:
                if doc.embedding:
                    embeddings.append(doc.embedding)
                else:
                    # Generate for this document
                    emb = self._generate_embeddings([doc.content])[0]
                    embeddings.append(emb)

            # Add to collection in batches
            with self._pool.get_client() as client:
                collection = self._get_or_create_collection(client, collection_name)

                added_count = 0
                for i in range(0, len(documents), batch_size):
                    batch_end = min(i + batch_size, len(documents))
                    logger.debug(
                        f"Processing batch {i // batch_size + 1}: " f"documents {i} to {batch_end}"
                    )

                    collection.add(
                        ids=ids[i:batch_end],
                        embeddings=embeddings[i:batch_end],
                        documents=contents[i:batch_end],
                        metadatas=metadatas[i:batch_end],
                    )
                    added_count += batch_end - i

                logger.info(f"Successfully added {added_count} documents")
                return {
                    "status": "success",
                    "added": added_count,
                    "collection": collection_name or self.settings.collection_name,
                }

        except ValidationError:
            raise
        except EmbeddingError:
            raise
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise CollectionError(f"Failed to add documents: {e}")

    def query(
        self, query_request: QueryRequest, collection_name: str | None = None
    ) -> list[QueryResult]:
        """
        Query the vector store.

        Args:
            query_request: Query parameters
            collection_name: Collection to query

        Returns:
            List of query results

        Raises:
            QueryError: If query fails
        """
        logger.info(f"Querying collection for {query_request.n_results} results")

        try:
            # Prepare query embedding
            if query_request.query_text:
                query_embeddings = self._generate_embeddings([query_request.query_text])
            elif query_request.query_embedding:
                query_embeddings = [query_request.query_embedding]
            else:
                raise ValidationError("No query text or embedding provided")

            # Execute query
            with self._pool.get_client() as client:
                collection = self._get_or_create_collection(client, collection_name)

                results = collection.query(
                    query_embeddings=query_embeddings,
                    n_results=query_request.n_results,
                    where=query_request.where,
                    where_document=query_request.where_document,
                    include=["documents", "metadatas", "distances"]
                    + (["embeddings"] if query_request.include_embeddings else []),
                )

                # Parse results
                query_results = []
                if results["ids"] and results["ids"][0]:
                    for i, doc_id in enumerate(results["ids"][0]):
                        result = QueryResult(
                            id=doc_id,
                            content=results["documents"][0][i],
                            metadata=results["metadatas"][0][i] or {},
                            distance=results["distances"][0][i],
                            embedding=(
                                results["embeddings"][0][i]
                                if query_request.include_embeddings
                                else None
                            ),
                        )
                        query_results.append(result)

                logger.info(f"Query returned {len(query_results)} results")
                return query_results

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise QueryError(f"Query failed: {e}")

    def update_documents(
        self, documents: list[Document], collection_name: str | None = None
    ) -> dict[str, Any]:
        """
        Update existing documents in the vector store.

        Args:
            documents: List of documents to update
            collection_name: Target collection name

        Returns:
            Dict with operation results

        Raises:
            ValidationError: If documents are invalid
            CollectionError: If update fails
        """
        if not documents:
            raise ValidationError("Documents list cannot be empty")

        logger.info(f"Updating {len(documents)} documents")

        try:
            # Extract data
            ids = [doc.id for doc in documents]
            contents = [doc.content for doc in documents]
            metadatas = [doc.metadata for doc in documents]

            # Generate embeddings
            embeddings = [
                doc.embedding if doc.embedding else self._generate_embeddings([doc.content])[0]
                for doc in documents
            ]

            # Update collection
            with self._pool.get_client() as client:
                collection = self._get_or_create_collection(client, collection_name)

                collection.update(
                    ids=ids,
                    embeddings=embeddings,
                    documents=contents,
                    metadatas=metadatas,
                )

                logger.info(f"Successfully updated {len(documents)} documents")
                return {
                    "status": "success",
                    "updated": len(documents),
                    "collection": collection_name or self.settings.collection_name,
                }

        except Exception as e:
            logger.error(f"Failed to update documents: {e}")
            raise CollectionError(f"Failed to update documents: {e}")

    def delete_documents(
        self,
        ids: list[str] | None = None,
        where: dict[str, Any] | None = None,
        collection_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Delete documents from the vector store.

        Args:
            ids: List of document IDs to delete
            where: Metadata filter for deletion
            collection_name: Target collection name

        Returns:
            Dict with operation results

        Raises:
            ValidationError: If neither ids nor where is provided
            CollectionError: If deletion fails
        """
        if not ids and not where:
            raise ValidationError("Either ids or where filter must be provided")

        logger.info(f"Deleting documents (ids: {ids}, where: {where})")

        try:
            with self._pool.get_client() as client:
                collection = self._get_or_create_collection(client, collection_name)

                collection.delete(ids=ids, where=where)

                logger.info("Documents deleted successfully")
                return {
                    "status": "success",
                    "collection": collection_name or self.settings.collection_name,
                }

        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            raise CollectionError(f"Failed to delete documents: {e}")

    def get_collection_info(self, collection_name: str | None = None) -> CollectionInfo:
        """
        Get information about a collection.

        Args:
            collection_name: Collection name

        Returns:
            CollectionInfo with collection details

        Raises:
            CollectionError: If operation fails
        """
        try:
            with self._pool.get_client() as client:
                collection = self._get_or_create_collection(client, collection_name)

                return CollectionInfo(
                    name=collection.name,
                    count=collection.count(),
                    metadata=collection.metadata or {},
                )

        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            raise CollectionError(f"Failed to get collection info: {e}")

    def health_check(self) -> HealthStatus:
        """
        Perform health check on vector store.

        Returns:
            HealthStatus with check results
        """
        start_time = time.time()

        try:
            with self._pool.get_client() as client:
                # Try to heartbeat
                heartbeat = client.heartbeat()

                latency_ms = (time.time() - start_time) * 1000

                logger.info(f"Health check passed (latency: {latency_ms:.2f}ms)")

                return HealthStatus(
                    status="healthy",
                    details={
                        "heartbeat": heartbeat,
                        "connection_pool": {
                            "max_connections": self._pool._max_connections,
                            "active_connections": self._pool._active_connections,
                        },
                    },
                    latency_ms=latency_ms,
                )

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthStatus(
                status="unhealthy",
                details={"error": str(e)},
            )

    def close(self):
        """Close all connections and cleanup resources."""
        logger.info("Closing vector store")
        self._pool.close_all()
        logger.info("Vector store closed")
