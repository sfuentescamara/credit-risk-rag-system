"""Data models for vector database operations."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Document(BaseModel):
    """Document model for embedding storage."""

    id: str = Field(..., description="Unique document identifier")
    content: str = Field(..., description="Document text content")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    embedding: list[float] | None = Field(default=None, description="Document embedding vector")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content is not empty."""
        if not v or not v.strip():
            raise ValueError("Document content cannot be empty")
        return v

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate ID is not empty."""
        if not v or not v.strip():
            raise ValueError("Document ID cannot be empty")
        return v


class QueryResult(BaseModel):
    """Query result model."""

    id: str = Field(..., description="Document identifier")
    content: str = Field(..., description="Document content")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    distance: float = Field(..., description="Distance/similarity score")
    embedding: list[float] | None = Field(default=None, description="Document embedding vector")


class QueryRequest(BaseModel):
    """Query request model."""

    query_text: str | None = Field(default=None, description="Text query to search for")
    query_embedding: list[float] | None = Field(
        default=None, description="Embedding vector to search with"
    )
    n_results: int = Field(default=5, ge=1, le=100, description="Number of results")
    where: dict[str, Any] | None = Field(default=None, description="Metadata filter conditions")
    where_document: dict[str, Any] | None = Field(
        default=None, description="Document content filter conditions"
    )
    include_embeddings: bool = Field(default=False, description="Include embeddings in results")

    @field_validator("query_text", "query_embedding")
    @classmethod
    def validate_query(cls, v, info):
        """Ensure at least one query type is provided."""
        # This will be checked in the root validator
        return v

    def model_post_init(self, __context):
        """Validate that at least one query type is provided."""
        if not self.query_text and not self.query_embedding:
            raise ValueError("Either query_text or query_embedding must be provided")


class BatchOperation(BaseModel):
    """Batch operation model."""

    documents: list[Document] = Field(..., description="List of documents")
    batch_size: int = Field(default=100, ge=1, le=1000, description="Batch processing size")


class CollectionInfo(BaseModel):
    """Collection information model."""

    name: str = Field(..., description="Collection name")
    count: int = Field(..., description="Number of documents")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Collection metadata")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")


class HealthStatus(BaseModel):
    """Health check status model."""

    status: str = Field(..., description="Health status (healthy/unhealthy)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional health details")
    latency_ms: float | None = Field(default=None, description="Response latency in milliseconds")
