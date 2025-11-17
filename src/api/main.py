"""
Main FastAPI application for Credit Risk RAG System.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.data import VectorStore, get_chroma_settings
from src.api.routes import router as vector_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Global vector store instance
vector_store: VectorStore = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    global vector_store
    logger.info("Starting up Credit Risk RAG System...")

    try:
        # Initialize vector store
        settings = get_chroma_settings()
        vector_store = VectorStore(settings=settings)
        logger.info("Vector store initialized successfully")

        yield

    finally:
        # Shutdown
        logger.info("Shutting down Credit Risk RAG System...")
        if vector_store:
            vector_store.close()
        logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Credit Risk RAG System",
    description="A sophisticated Credit Risk Assessment System powered by RAG",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(vector_router)


@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """
    Root endpoint.

    Returns:
        Dict with welcome message
    """
    return {
        "message": "Credit Risk RAG System API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.

    Returns:
        Dict with health status
    """
    return {"status": "healthy", "service": "api"}


@app.get("/health/chromadb", tags=["Health"])
async def chromadb_health() -> Dict:
    """
    ChromaDB health check endpoint.

    Returns:
        Dict with ChromaDB health status

    Raises:
        HTTPException: If ChromaDB is unhealthy
    """
    try:
        if not vector_store:
            raise HTTPException(
                status_code=503, detail="Vector store not initialized"
            )

        health_status = vector_store.health_check()

        if health_status.status != "healthy":
            raise HTTPException(
                status_code=503,
                detail={
                    "status": health_status.status,
                    "details": health_status.details,
                },
            )

        return {
            "status": health_status.status,
            "timestamp": health_status.timestamp.isoformat(),
            "latency_ms": health_status.latency_ms,
            "details": health_status.details,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/health/ready", tags=["Health"])
async def readiness_check() -> Dict[str, str]:
    """
    Readiness check endpoint (for Kubernetes).

    Returns:
        Dict with readiness status

    Raises:
        HTTPException: If service is not ready
    """
    try:
        if not vector_store:
            raise HTTPException(
                status_code=503, detail="Vector store not initialized"
            )

        # Check ChromaDB
        health_status = vector_store.health_check()
        if health_status.status != "healthy":
            raise HTTPException(status_code=503, detail="ChromaDB not ready")

        return {"status": "ready"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503, detail=f"Service not ready: {str(e)}"
        )


@app.get("/health/live", tags=["Health"])
async def liveness_check() -> Dict[str, str]:
    """
    Liveness check endpoint (for Kubernetes).

    Returns:
        Dict with liveness status
    """
    return {"status": "alive"}
