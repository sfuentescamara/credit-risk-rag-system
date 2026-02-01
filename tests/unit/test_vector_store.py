"""Unit tests for vector store client."""

from unittest.mock import Mock, patch

import pytest

from src.data import (
    ChromaDBSettings,
    Document,
    EmbeddingError,
    QueryRequest,
    QueryResult,
    ValidationError,
    VectorStore,
)


@pytest.fixture
def mock_settings():
    """Create mock ChromaDB settings."""
    return ChromaDBSettings(
        host="localhost",
        port=8001,
        collection_name="test_collection",
        embedding_function="sentence-transformers/all-MiniLM-L6-v2",
        max_connections=5,
        batch_size=10,
    )


@pytest.fixture
def mock_embedding_model():
    """Create mock embedding model."""
    model = Mock()
    model.encode.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    return model


@pytest.fixture
def mock_chroma_client():
    """Create mock ChromaDB client."""
    client = Mock()
    collection = Mock()
    collection.name = "test_collection"
    collection.count.return_value = 0
    collection.metadata = {}
    client.get_or_create_collection.return_value = collection
    client.heartbeat.return_value = 1234567890
    return client


@pytest.fixture
def vector_store(mock_settings, mock_embedding_model):
    """Create vector store with mocked dependencies."""
    with patch("src.data.vector_store.SentenceTransformer") as mock_st:
        mock_st.return_value = mock_embedding_model
        store = VectorStore(settings=mock_settings)
        store._embedding_model = mock_embedding_model
        yield store


class TestVectorStoreInit:
    """Test vector store initialization."""

    def test_init_with_settings(self, mock_settings):
        """Test initialization with custom settings."""
        with patch("src.data.vector_store.SentenceTransformer"):
            store = VectorStore(settings=mock_settings)
            assert store.settings == mock_settings
            assert store.settings.collection_name == "test_collection"

    def test_init_with_default_settings(self):
        """Test initialization with default settings."""
        with patch("src.data.vector_store.SentenceTransformer"):
            with patch("src.data.config.get_chroma_settings") as mock_get:
                mock_get.return_value = ChromaDBSettings()
                store = VectorStore()
                assert store.settings is not None


class TestEmbeddingGeneration:
    """Test embedding generation."""

    def test_generate_embeddings(self, vector_store):
        """Test successful embedding generation."""
        texts = ["test document 1", "test document 2"]
        embeddings = vector_store._generate_embeddings(texts)

        assert len(embeddings) == 2
        vector_store._embedding_model.encode.assert_called_once()

    def test_generate_embeddings_error(self, vector_store):
        """Test embedding generation error handling."""
        vector_store._embedding_model.encode.side_effect = Exception("Model error")

        with pytest.raises(EmbeddingError, match="Failed to generate embeddings"):
            vector_store._generate_embeddings(["test"])


class TestAddDocuments:
    """Test adding documents."""

    def test_add_documents_success(self, vector_store, mock_chroma_client):
        """Test successful document addition."""
        documents = [
            Document(id="1", content="Test doc 1", metadata={"type": "test"}),
            Document(id="2", content="Test doc 2", metadata={"type": "test"}),
        ]

        with patch.object(vector_store._pool, "get_client") as mock_get_client:
            mock_get_client.return_value.__enter__.return_value = mock_chroma_client

            result = vector_store.add_documents(documents)

            assert result["status"] == "success"
            assert result["added"] == 2
            mock_chroma_client.get_or_create_collection.assert_called_once()

    def test_add_documents_empty_list(self, vector_store):
        """Test adding empty document list."""
        with pytest.raises(ValidationError, match="Documents list cannot be empty"):
            vector_store.add_documents([])

    def test_add_documents_with_embeddings(self, vector_store, mock_chroma_client):
        """Test adding documents with pre-computed embeddings."""
        documents = [
            Document(
                id="1",
                content="Test",
                metadata={},
                embedding=[0.1, 0.2, 0.3],
            )
        ]

        with patch.object(vector_store._pool, "get_client") as mock_get_client:
            mock_get_client.return_value.__enter__.return_value = mock_chroma_client

            result = vector_store.add_documents(documents)
            assert result["status"] == "success"

    def test_add_documents_batch_processing(self, vector_store, mock_chroma_client):
        """Test batch processing of documents."""
        documents = [Document(id=str(i), content=f"Doc {i}", metadata={}) for i in range(25)]

        with patch.object(vector_store._pool, "get_client") as mock_get_client:
            mock_get_client.return_value.__enter__.return_value = mock_chroma_client

            result = vector_store.add_documents(documents, batch_size=10)

            assert result["added"] == 25
            # Should be called 3 times (10, 10, 5)
            collection = mock_chroma_client.get_or_create_collection.return_value
            assert collection.add.call_count == 3


class TestQueryDocuments:
    """Test querying documents."""

    def test_query_with_text(self, vector_store, mock_chroma_client):
        """Test query with text input."""
        mock_chroma_client.get_or_create_collection.return_value.query.return_value = {
            "ids": [["1", "2"]],
            "documents": [["Doc 1", "Doc 2"]],
            "metadatas": [[{"type": "test"}, {"type": "test"}]],
            "distances": [[0.1, 0.2]],
            "embeddings": None,
        }

        query = QueryRequest(query_text="test query", n_results=2)

        with patch.object(vector_store._pool, "get_client") as mock_get_client:
            mock_get_client.return_value.__enter__.return_value = mock_chroma_client

            results = vector_store.query(query)

            assert len(results) == 2
            assert isinstance(results[0], QueryResult)
            assert results[0].id == "1"
            assert results[0].content == "Doc 1"

    def test_query_with_embedding(self, vector_store, mock_chroma_client):
        """Test query with embedding vector."""
        mock_chroma_client.get_or_create_collection.return_value.query.return_value = {
            "ids": [["1"]],
            "documents": [["Doc 1"]],
            "metadatas": [[{"type": "test"}]],
            "distances": [[0.1]],
            "embeddings": None,
        }

        query = QueryRequest(query_embedding=[0.1, 0.2, 0.3], n_results=1)

        with patch.object(vector_store._pool, "get_client") as mock_get_client:
            mock_get_client.return_value.__enter__.return_value = mock_chroma_client

            results = vector_store.query(query)
            assert len(results) == 1

    def test_query_with_filters(self, vector_store, mock_chroma_client):
        """Test query with metadata filters."""
        mock_chroma_client.get_or_create_collection.return_value.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
            "embeddings": None,
        }

        query = QueryRequest(
            query_text="test",
            n_results=5,
            where={"type": "financial"},
        )

        with patch.object(vector_store._pool, "get_client") as mock_get_client:
            mock_get_client.return_value.__enter__.return_value = mock_chroma_client

            _ = vector_store.query(query)
            collection = mock_chroma_client.get_or_create_collection.return_value
            collection.query.assert_called_once()


class TestUpdateDocuments:
    """Test updating documents."""

    def test_update_documents_success(self, vector_store, mock_chroma_client):
        """Test successful document update."""
        documents = [Document(id="1", content="Updated content", metadata={"updated": True})]

        with patch.object(vector_store._pool, "get_client") as mock_get_client:
            mock_get_client.return_value.__enter__.return_value = mock_chroma_client

            result = vector_store.update_documents(documents)

            assert result["status"] == "success"
            assert result["updated"] == 1
            collection = mock_chroma_client.get_or_create_collection.return_value
            collection.update.assert_called_once()

    def test_update_documents_empty_list(self, vector_store):
        """Test updating empty document list."""
        with pytest.raises(ValidationError, match="Documents list cannot be empty"):
            vector_store.update_documents([])


class TestDeleteDocuments:
    """Test deleting documents."""

    def test_delete_by_ids(self, vector_store, mock_chroma_client):
        """Test deletion by document IDs."""
        with patch.object(vector_store._pool, "get_client") as mock_get_client:
            mock_get_client.return_value.__enter__.return_value = mock_chroma_client

            result = vector_store.delete_documents(ids=["1", "2"])

            assert result["status"] == "success"
            collection = mock_chroma_client.get_or_create_collection.return_value
            collection.delete.assert_called_once_with(ids=["1", "2"], where=None)

    def test_delete_by_filter(self, vector_store, mock_chroma_client):
        """Test deletion by metadata filter."""
        with patch.object(vector_store._pool, "get_client") as mock_get_client:
            mock_get_client.return_value.__enter__.return_value = mock_chroma_client

            result = vector_store.delete_documents(where={"type": "obsolete"})

            assert result["status"] == "success"

    def test_delete_no_params(self, vector_store):
        """Test deletion without parameters."""
        with pytest.raises(ValidationError, match="Either ids or where filter must be provided"):
            vector_store.delete_documents()


class TestCollectionInfo:
    """Test collection information retrieval."""

    def test_get_collection_info(self, vector_store, mock_chroma_client):
        """Test getting collection information."""
        with patch.object(vector_store._pool, "get_client") as mock_get_client:
            mock_get_client.return_value.__enter__.return_value = mock_chroma_client

            info = vector_store.get_collection_info()

            assert info.name == "test_collection"
            assert info.count == 0


class TestHealthCheck:
    """Test health check functionality."""

    def test_health_check_healthy(self, vector_store, mock_chroma_client):
        """Test successful health check."""
        with patch.object(vector_store._pool, "get_client") as mock_get_client:
            mock_get_client.return_value.__enter__.return_value = mock_chroma_client

            status = vector_store.health_check()

            assert status.status == "healthy"
            assert status.latency_ms is not None
            mock_chroma_client.heartbeat.assert_called_once()

    def test_health_check_unhealthy(self, vector_store, mock_chroma_client):
        """Test health check failure."""
        mock_chroma_client.heartbeat.side_effect = Exception("Connection failed")

        with patch.object(vector_store._pool, "get_client") as mock_get_client:
            mock_get_client.return_value.__enter__.return_value = mock_chroma_client

            status = vector_store.health_check()

            assert status.status == "unhealthy"
            assert "error" in status.details


class TestConnectionPool:
    """Test connection pooling."""

    def test_connection_pool_reuse(self, vector_store):
        """Test connection pool reuses connections."""
        # This tests the basic pool functionality
        assert vector_store._pool._max_connections == 5
        assert vector_store._pool._active_connections == 0

    def test_close_connections(self, vector_store):
        """Test closing all connections."""
        vector_store.close()
        assert vector_store._pool._active_connections == 0
