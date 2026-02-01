"""
Unit tests for data models.
"""

import pytest
from pydantic import ValidationError as PydanticValidationError

from src.data import Document, QueryRequest, QueryResult


class TestDocument:
    """Test Document model."""

    def test_valid_document(self):
        """Test creating valid document."""
        doc = Document(
            id="123",
            content="Test content",
            metadata={"type": "test", "score": 0.95},
        )

        assert doc.id == "123"
        assert doc.content == "Test content"
        assert doc.metadata["type"] == "test"
        assert doc.embedding is None

    def test_document_with_embedding(self):
        """Test document with embedding vector."""
        doc = Document(
            id="123",
            content="Test",
            embedding=[0.1, 0.2, 0.3],
        )

        assert len(doc.embedding) == 3

    def test_empty_content(self):
        """Test document with empty content."""
        with pytest.raises(PydanticValidationError):
            Document(id="123", content="")

    def test_empty_id(self):
        """Test document with empty ID."""
        with pytest.raises(PydanticValidationError):
            Document(id="", content="Test")

    def test_whitespace_content(self):
        """Test document with whitespace-only content."""
        with pytest.raises(PydanticValidationError):
            Document(id="123", content="   ")

    def test_default_metadata(self):
        """Test document with default empty metadata."""
        doc = Document(id="123", content="Test")
        assert doc.metadata == {}


class TestQueryRequest:
    """Test QueryRequest model."""

    def test_query_with_text(self):
        """Test query request with text."""
        query = QueryRequest(query_text="test query", n_results=5)

        assert query.query_text == "test query"
        assert query.n_results == 5
        assert query.query_embedding is None

    def test_query_with_embedding(self):
        """Test query request with embedding vector."""
        query = QueryRequest(
            query_embedding=[0.1, 0.2, 0.3],
            n_results=10,
        )

        assert len(query.query_embedding) == 3
        assert query.query_text is None

    def test_query_with_filters(self):
        """Test query request with filters."""
        query = QueryRequest(
            query_text="test",
            n_results=5,
            where={"type": "financial"},
            where_document={"$contains": "credit"},
        )

        assert query.where == {"type": "financial"}
        assert query.where_document == {"$contains": "credit"}

    def test_no_query_provided(self):
        """Test query request without text or embedding."""
        with pytest.raises(ValueError, match="Either query_text or query_embedding"):
            QueryRequest(n_results=5)

    def test_n_results_boundaries(self):
        """Test n_results validation."""
        # Valid range
        query = QueryRequest(query_text="test", n_results=1)
        assert query.n_results == 1

        query = QueryRequest(query_text="test", n_results=100)
        assert query.n_results == 100

        # Invalid values
        with pytest.raises(PydanticValidationError):
            QueryRequest(query_text="test", n_results=0)

        with pytest.raises(PydanticValidationError):
            QueryRequest(query_text="test", n_results=101)

    def test_include_embeddings(self):
        """Test include_embeddings flag."""
        query = QueryRequest(
            query_text="test",
            n_results=5,
            include_embeddings=True,
        )

        assert query.include_embeddings is True


class TestQueryResult:
    """Test QueryResult model."""

    def test_valid_result(self):
        """Test creating valid query result."""
        result = QueryResult(
            id="123",
            content="Test content",
            metadata={"type": "test"},
            distance=0.25,
        )

        assert result.id == "123"
        assert result.content == "Test content"
        assert result.distance == 0.25
        assert result.embedding is None

    def test_result_with_embedding(self):
        """Test result with embedding vector."""
        result = QueryResult(
            id="123",
            content="Test",
            metadata={},
            distance=0.1,
            embedding=[0.1, 0.2, 0.3],
        )

        assert len(result.embedding) == 3

    def test_default_metadata(self):
        """Test result with default metadata."""
        result = QueryResult(
            id="123",
            content="Test",
            distance=0.5,
        )

        assert result.metadata == {}
