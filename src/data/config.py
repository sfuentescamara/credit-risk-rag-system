"""
Configuration management for ChromaDB vector database.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class ChromaDBSettings(BaseSettings):
    """ChromaDB configuration settings."""

    host: str = Field(default="localhost", description="ChromaDB host")
    port: int = Field(default=8001, description="ChromaDB port")
    url: Optional[str] = Field(
        default=None, description="Full ChromaDB URL (overrides host/port)"
    )
    auth_credentials: Optional[str] = Field(
        default=None, description="Authentication credentials (username:password)"
    )
    auth_provider: str = Field(
        default="chromadb.auth.basic.BasicAuthServerProvider",
        description="Authentication provider",
    )
    collection_name: str = Field(
        default="credit_risk_documents", description="Default collection name"
    )
    embedding_function: str = Field(
        default="sentence-transformers/all-mpnet-base-v2",
        description="Embedding model name",
    )
    # Connection pooling settings
    max_connections: int = Field(
        default=10, description="Maximum number of connections in pool"
    )
    connection_timeout: int = Field(
        default=30, description="Connection timeout in seconds"
    )
    # Performance settings
    batch_size: int = Field(
        default=100, description="Default batch size for operations"
    )
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(
        default=1.0, description="Initial retry delay in seconds"
    )
    # Storage settings
    persist_directory: Optional[str] = Field(
        default="./data/chroma", description="Local persistence directory"
    )

    class Config:
        env_prefix = "CHROMA_"
        case_sensitive = False
        env_file = ".env"

    @property
    def connection_url(self) -> str:
        """Get the full connection URL."""
        if self.url:
            return self.url
        return f"http://{self.host}:{self.port}"


@lru_cache()
def get_chroma_settings() -> ChromaDBSettings:
    """
    Get cached ChromaDB settings instance.

    Returns:
        ChromaDBSettings: Singleton settings instance
    """
    return ChromaDBSettings()
