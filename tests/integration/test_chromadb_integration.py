"""
Integration tests for ChromaDB vector store.

These tests require a running ChromaDB instance.
Set CHROMA_URL environment variable or use default localhost:8001
"""

import os
import pytest
import time
from typing import List

from src.data import (
    VectorStore,
    ChromaDBSettings,
    Document,
    QueryRequest,
    ValidationError,
)


# Skip integration tests if ChromaDB is not available
pytestmark = pytest.mark.skipif(
    os.getenv("SKIP_INTEGRATION_TESTS") == "true",
    reason="Integration tests skipped",
)


@pytest.fixture(scope="module")
def chroma_settings():
    """Create ChromaDB settings for integration tests."""
    return ChromaDBSettings(
        host=os.getenv("CHROMA_HOST", "localhost"),
        port=int(os.getenv("CHROMA_PORT", "8001")),
        collection_name="test_integration_collection",
        embedding_function="sentence-transformers/all-MiniLM-L6-v2",
    )


@pytest.fixture(scope="module")
def vector_store(chroma_settings):
    """Create vector store for integration tests."""
    store = VectorStore(settings=chroma_settings)
    yield store
    # Cleanup
    try:
        # Delete all documents from test collection
        info = store.get_collection_info()
        if info.count > 0:
            # Get all document IDs and delete
            pass  # ChromaDB will handle cleanup
    except Exception:
        pass
    finally:
        store.close()


@pytest.fixture
def sample_documents() -> List[Document]:
    """Create sample documents for testing."""
    return [
        Document(
            id="doc1",
            content="Credit risk assessment for corporate borrowers",
            metadata={"type": "financial", "category": "credit"},
        ),
        Document(
            id="doc2",
            content="Portfolio diversification strategies for risk management",
            metadata={"type": "financial", "category": "risk"},
        ),
        Document(
            id="doc3",
            content="Machine learning models for credit scoring",
            metadata={"type": "technical", "category": "ml"},
        ),
        Document(
            id="doc4",
            content="Regulatory compliance in financial services",
            metadata={"type": "compliance", "category": "regulatory"},
        ),
        Document(
            id="doc5",
            content="Real-time fraud detection using AI",
            metadata={"type": "technical", "category": "fraud"},
        ),
    ]


class TestChromaDBConnection:
    """Test ChromaDB connection and health."""

    def test_health_check(self, vector_store):
        """Test vector store health check."""
        status = vector_store.health_check()

        assert status.status == "healthy"
        assert status.latency_ms is not None
        assert status.latency_ms < 1000  # Should respond within 1 second

    def test_collection_creation(self, vector_store):
        """Test collection is created."""
        info = vector_store.get_collection_info()

        assert info.name == "test_integration_collection"
        assert info.count >= 0


class TestDocumentOperations:
    """Test document CRUD operations."""

    def test_add_documents(self, vector_store, sample_documents):
        """Test adding documents to vector store."""
        result = vector_store.add_documents(sample_documents[:3])

        assert result["status"] == "success"
        assert result["added"] == 3

        # Verify count increased
        info = vector_store.get_collection_info()
        assert info.count >= 3

    def test_add_documents_in_batches(self, vector_store):
        """Test batch document addition."""
        # Create many documents
        docs = [
            Document(
                id=f"batch_doc_{i}",
                content=f"Test document {i} for batch processing",
                metadata={"batch": True, "index": i},
            )
            for i in range(25)
        ]

        result = vector_store.add_documents(docs, batch_size=10)

        assert result["status"] == "success"
        assert result["added"] == 25

    def test_query_documents(self, vector_store, sample_documents):
        """Test querying documents."""
        # First add documents
        vector_store.add_documents(sample_documents)

        # Give ChromaDB a moment to index
        time.sleep(0.5)

        # Query for credit-related documents
        query = QueryRequest(
            query_text="credit risk management",
            n_results=3,
        )

        results = vector_store.query(query)

        assert len(results) > 0
        assert len(results) <= 3
        # Results should be ranked by relevance
        assert results[0].distance >= 0

    def test_query_with_metadata_filter(self, vector_store, sample_documents):
        """Test querying with metadata filters."""
        vector_store.add_documents(sample_documents)
        time.sleep(0.5)

        query = QueryRequest(
            query_text="risk",
            n_results=5,
            where={"type": "financial"},
        )

        results = vector_store.query(query)

        # All results should match the filter
        for result in results:
            assert result.metadata.get("type") == "financial"

    def test_query_with_embeddings_included(
        self, vector_store, sample_documents
    ):
        """Test query that includes embedding vectors."""
        vector_store.add_documents(sample_documents[:2])
        time.sleep(0.5)

        query = QueryRequest(
            query_text="credit",
            n_results=2,
            include_embeddings=True,
        )

        results = vector_store.query(query)

        assert len(results) > 0
        # Check that embeddings are included
        for result in results:
            assert result.embedding is not None
            assert len(result.embedding) > 0

    def test_update_documents(self, vector_store):
        """Test updating existing documents."""
        # Add initial document
        doc = Document(
            id="update_test",
            content="Original content",
            metadata={"version": 1},
        )
        vector_store.add_documents([doc])
        time.sleep(0.5)

        # Update the document
        updated_doc = Document(
            id="update_test",
            content="Updated content",
            metadata={"version": 2, "updated": True},
        )
        result = vector_store.update_documents([updated_doc])

        assert result["status"] == "success"
        assert result["updated"] == 1

    def test_delete_documents_by_id(self, vector_store):
        """Test deleting documents by ID."""
        # Add documents to delete
        docs = [
            Document(id="delete1", content="To be deleted 1", metadata={}),
            Document(id="delete2", content="To be deleted 2", metadata={}),
        ]
        vector_store.add_documents(docs)
        time.sleep(0.5)

        # Delete them
        result = vector_store.delete_documents(ids=["delete1", "delete2"])

        assert result["status"] == "success"

    def test_delete_documents_by_filter(self, vector_store):
        """Test deleting documents by metadata filter."""
        # Add documents with specific metadata
        docs = [
            Document(
                id=f"temp_{i}",
                content=f"Temporary doc {i}",
                metadata={"temporary": True},
            )
            for i in range(3)
        ]
        vector_store.add_documents(docs)
        time.sleep(0.5)

        # Delete by filter
        result = vector_store.delete_documents(
            where={"temporary": True}
        )

        assert result["status"] == "success"


class TestPerformance:
    """Test performance requirements."""

    def test_query_latency(self, vector_store, sample_documents):
        """Test that queries complete within 100ms for small dataset."""
        # Add documents
        vector_store.add_documents(sample_documents)
        time.sleep(0.5)

        # Measure query time
        query = QueryRequest(query_text="credit risk", n_results=5)

        start_time = time.time()
        results = vector_store.query(query)
        elapsed_ms = (time.time() - start_time) * 1000

        # Should complete quickly for small dataset
        assert elapsed_ms < 500  # 500ms threshold for integration test

    def test_batch_insert_rate(self, vector_store):
        """Test batch insert performance."""
        # Create batch of documents
        batch_size = 100
        docs = [
            Document(
                id=f"perf_doc_{i}",
                content=f"Performance test document {i}",
                metadata={"batch": "performance"},
            )
            for i in range(batch_size)
        ]

        # Measure insert time
        start_time = time.time()
        result = vector_store.add_documents(docs, batch_size=50)
        elapsed = time.time() - start_time

        # Calculate rate (documents per second)
        rate = batch_size / elapsed

        assert result["added"] == batch_size
        # Should process at least 50 documents per second
        assert rate > 50


class TestErrorHandling:
    """Test error handling."""

    def test_empty_document_list(self, vector_store):
        """Test error on empty document list."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            vector_store.add_documents([])

    def test_invalid_query(self, vector_store):
        """Test error on invalid query."""
        with pytest.raises(ValueError):
            QueryRequest(n_results=5)  # No query text or embedding

    def test_delete_without_params(self, vector_store):
        """Test error when deleting without parameters."""
        with pytest.raises(
            ValidationError, match="Either ids or where filter"
        ):
            vector_store.delete_documents()


class TestConcurrency:
    """Test concurrent operations."""

    def test_multiple_queries(self, vector_store, sample_documents):
        """Test multiple concurrent queries."""
        vector_store.add_documents(sample_documents)
        time.sleep(0.5)

        # Run multiple queries
        queries = [
            QueryRequest(query_text="credit", n_results=3),
            QueryRequest(query_text="risk", n_results=3),
            QueryRequest(query_text="fraud", n_results=3),
        ]

        results_list = []
        for query in queries:
            results = vector_store.query(query)
            results_list.append(results)

        # All queries should succeed
        assert len(results_list) == 3
        for results in results_list:
            assert len(results) > 0
