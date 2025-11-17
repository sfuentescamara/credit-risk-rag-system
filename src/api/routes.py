"""
API routes for vector store operations.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from src.data import Document, QueryRequest, QueryResult, VectorStore

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/vector", tags=["Vector Store"])


def get_vector_store() -> VectorStore:
    """
    Get the global vector store instance.

    Returns:
        VectorStore instance

    Raises:
        HTTPException: If vector store not initialized
    """
    from src.api.main import vector_store

    if not vector_store:
        raise HTTPException(
            status_code=503, detail="Vector store not initialized"
        )
    return vector_store


@router.post("/documents", response_model=Dict[str, Any])
async def add_documents(
    documents: List[Document],
    collection_name: Optional[str] = None,
    batch_size: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Add documents to the vector store.

    Args:
        documents: List of documents to add
        collection_name: Target collection name (optional)
        batch_size: Batch size for processing (optional)

    Returns:
        Operation result with status and count
    """
    try:
        store = get_vector_store()
        result = store.add_documents(
            documents=documents,
            collection_name=collection_name,
            batch_size=batch_size,
        )
        return result

    except Exception as e:
        logger.error(f"Failed to add documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=List[QueryResult])
async def query_documents(
    query_request: QueryRequest, collection_name: Optional[str] = None
) -> List[QueryResult]:
    """
    Query documents from the vector store.

    Args:
        query_request: Query parameters
        collection_name: Collection to query (optional)

    Returns:
        List of matching documents
    """
    try:
        store = get_vector_store()
        results = store.query(
            query_request=query_request, collection_name=collection_name
        )
        return results

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/documents", response_model=Dict[str, Any])
async def update_documents(
    documents: List[Document], collection_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update existing documents in the vector store.

    Args:
        documents: List of documents to update
        collection_name: Target collection name (optional)

    Returns:
        Operation result with status and count
    """
    try:
        store = get_vector_store()
        result = store.update_documents(
            documents=documents, collection_name=collection_name
        )
        return result

    except Exception as e:
        logger.error(f"Failed to update documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents", response_model=Dict[str, Any])
async def delete_documents(
    ids: Optional[List[str]] = Query(default=None),
    where: Optional[Dict[str, Any]] = None,
    collection_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Delete documents from the vector store.

    Args:
        ids: List of document IDs to delete
        where: Metadata filter for deletion
        collection_name: Target collection name (optional)

    Returns:
        Operation result with status
    """
    try:
        store = get_vector_store()
        result = store.delete_documents(
            ids=ids, where=where, collection_name=collection_name
        )
        return result

    except Exception as e:
        logger.error(f"Failed to delete documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections/{collection_name}", response_model=Dict[str, Any])
async def get_collection_info(collection_name: str) -> Dict[str, Any]:
    """
    Get information about a collection.

    Args:
        collection_name: Collection name

    Returns:
        Collection information
    """
    try:
        store = get_vector_store()
        info = store.get_collection_info(collection_name=collection_name)
        return {
            "name": info.name,
            "count": info.count,
            "metadata": info.metadata,
        }

    except Exception as e:
        logger.error(f"Failed to get collection info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
