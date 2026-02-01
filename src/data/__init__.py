"""
Data module for vector database operations.
"""

from .config import ChromaDBSettings, get_chroma_settings
from .exceptions import (
    CollectionError,
    ConnectionError,
    EmbeddingError,
    QueryError,
    ValidationError,
    VectorDBError,
)
from .models import (
    BatchOperation,
    CollectionInfo,
    Document,
    HealthStatus,
    QueryRequest,
    QueryResult,
)
from .vector_store import VectorStore

__all__ = [
    # Config
    "ChromaDBSettings",
    "get_chroma_settings",
    # Exceptions
    "VectorDBError",
    "ConnectionError",
    "CollectionError",
    "EmbeddingError",
    "QueryError",
    "ValidationError",
    # Models
    "Document",
    "QueryResult",
    "QueryRequest",
    "BatchOperation",
    "CollectionInfo",
    "HealthStatus",
    # Client
    "VectorStore",
]
