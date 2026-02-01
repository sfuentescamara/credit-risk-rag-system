"""
Custom exceptions for vector database operations.
"""


class VectorDBError(Exception):
    """Base exception for vector database errors."""

    pass


class ConnectionError(VectorDBError):
    """Raised when connection to vector database fails."""

    pass


class CollectionError(VectorDBError):
    """Raised when collection operations fail."""

    pass


class EmbeddingError(VectorDBError):
    """Raised when embedding operations fail."""

    pass


class QueryError(VectorDBError):
    """Raised when query operations fail."""

    pass


class ValidationError(VectorDBError):
    """Raised when input validation fails."""

    pass
