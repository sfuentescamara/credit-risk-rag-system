#!/usr/bin/env python3
"""
Example script demonstrating ChromaDB vector store usage.

This script shows how to:
1. Initialize the vector store
2. Add documents
3. Query for similar documents
4. Update and delete documents
5. Check health status
"""

import os
import sys

# Add src to path before importing from src
current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, "..")
sys.path.insert(0, parent_dir)

from src.data import ChromaDBSettings, Document, QueryRequest, VectorStore  # noqa: E402


def main():
    """Run example vector store operations."""
    print("=" * 60)
    print("ChromaDB Vector Store Example")
    print("=" * 60)

    # 1. Initialize vector store
    print("\n1. Initializing vector store...")
    settings = ChromaDBSettings(
        host=os.getenv("CHROMA_HOST", "localhost"),
        port=int(os.getenv("CHROMA_PORT", "8001")),
        collection_name="example_collection",
    )
    store = VectorStore(settings=settings)
    print("✓ Vector store initialized")

    # 2. Check health
    print("\n2. Checking health...")
    health = store.health_check()
    print(f"✓ Status: {health.status}")
    print(f"  Latency: {health.latency_ms:.2f}ms")

    # 3. Add sample documents
    print("\n3. Adding sample documents...")
    documents = [
        Document(
            id="cr_001",
            content="Credit risk assessment involves evaluating the probability of default by analyzing borrower's financial statements and credit history.",
            metadata={
                "type": "definition",
                "category": "credit_risk",
                "importance": "high",
            },
        ),
        Document(
            id="cr_002",
            content="Portfolio diversification reduces overall risk by spreading investments across different assets, sectors, and geographies.",
            metadata={
                "type": "strategy",
                "category": "risk_management",
                "importance": "high",
            },
        ),
        Document(
            id="cr_003",
            content="Machine learning models can predict credit defaults with higher accuracy by analyzing patterns in historical data.",
            metadata={
                "type": "technology",
                "category": "ml_models",
                "importance": "medium",
            },
        ),
        Document(
            id="cr_004",
            content="Basel III regulations require banks to maintain minimum capital ratios to ensure financial stability.",
            metadata={
                "type": "regulation",
                "category": "compliance",
                "importance": "high",
            },
        ),
        Document(
            id="cr_005",
            content="Real-time fraud detection systems use AI to identify suspicious transactions and prevent financial losses.",
            metadata={
                "type": "technology",
                "category": "fraud_detection",
                "importance": "medium",
            },
        ),
    ]

    result = store.add_documents(documents)
    print(f"✓ Added {result['added']} documents to collection")

    # 4. Get collection info
    print("\n4. Collection information...")
    info = store.get_collection_info()
    print(f"✓ Collection: {info.name}")
    print(f"  Total documents: {info.count}")

    # 5. Query documents
    print("\n5. Querying for 'credit risk assessment'...")
    query = QueryRequest(
        query_text="credit risk assessment and default prediction",
        n_results=3,
    )
    results = store.query(query)

    print(f"✓ Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n  Result {i}:")
        print(f"    ID: {result.id}")
        print(f"    Content: {result.content[:80]}...")
        print(f"    Distance: {result.distance:.4f}")
        print(f"    Category: {result.metadata.get('category')}")

    # 6. Query with metadata filter
    print("\n6. Querying with metadata filter (type='technology')...")
    query = QueryRequest(
        query_text="artificial intelligence and machine learning",
        n_results=5,
        where={"type": "technology"},
    )
    results = store.query(query)

    print(f"✓ Found {len(results)} technology-related results:")
    for result in results:
        print(f"  - {result.id}: {result.metadata.get('category')}")

    # 7. Update a document
    print("\n7. Updating document cr_003...")
    updated_doc = Document(
        id="cr_003",
        content="Advanced machine learning models, including neural networks and ensemble methods, can predict credit defaults with higher accuracy by analyzing complex patterns in historical data.",
        metadata={
            "type": "technology",
            "category": "ml_models",
            "importance": "high",
            "updated": True,
        },
    )
    result = store.update_documents([updated_doc])
    print(f"✓ Updated {result['updated']} document(s)")

    # 8. Delete a document
    print("\n8. Deleting document cr_005...")
    result = store.delete_documents(ids=["cr_005"])
    print("✓ Deleted document(s)")

    # 9. Final collection info
    print("\n9. Final collection information...")
    info = store.get_collection_info()
    print(f"✓ Collection: {info.name}")
    print(f"  Total documents: {info.count}")

    # 10. Cleanup
    print("\n10. Cleaning up...")
    store.close()
    print("✓ Vector store closed")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExample interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
