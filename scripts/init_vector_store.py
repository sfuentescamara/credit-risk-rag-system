#!/usr/bin/env python3
"""
Initialize ChromaDB vector store with sample data.

This script sets up the vector store with initial credit risk documents
for development and testing purposes.
"""

import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data import VectorStore, Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


SAMPLE_DOCUMENTS = [
    Document(
        id="credit_risk_101",
        content="Credit risk is the possibility of a loss resulting from a borrower's failure to repay a loan or meet contractual obligations.",
        metadata={
            "category": "definitions",
            "topic": "credit_risk",
            "level": "basic",
        },
    ),
    Document(
        id="pd_lgd_ead",
        content="The three key components of credit risk are: Probability of Default (PD), Loss Given Default (LGD), and Exposure at Default (EAD).",
        metadata={
            "category": "concepts",
            "topic": "credit_risk_components",
            "level": "intermediate",
        },
    ),
    Document(
        id="credit_scoring",
        content="Credit scoring models use statistical techniques to assess the creditworthiness of borrowers based on historical data and current financial information.",
        metadata={
            "category": "methodologies",
            "topic": "scoring",
            "level": "intermediate",
        },
    ),
    Document(
        id="basel_framework",
        content="The Basel framework provides international regulatory standards for banks, including minimum capital requirements based on credit, market, and operational risks.",
        metadata={
            "category": "regulations",
            "topic": "basel",
            "level": "advanced",
        },
    ),
    Document(
        id="portfolio_risk",
        content="Portfolio credit risk management involves diversification, concentration limits, and correlation analysis to optimize risk-adjusted returns.",
        metadata={
            "category": "strategies",
            "topic": "portfolio_management",
            "level": "advanced",
        },
    ),
]


def main():
    """Initialize vector store with sample documents."""
    logger.info("Starting vector store initialization...")

    try:
        # Initialize vector store
        logger.info("Connecting to ChromaDB...")
        store = VectorStore()

        # Check health
        health = store.health_check()
        if health.status != "healthy":
            logger.error(f"Vector store unhealthy: {health.details}")
            return 1

        logger.info(f"Vector store healthy (latency: {health.latency_ms:.2f}ms)")

        # Add sample documents
        logger.info(f"Adding {len(SAMPLE_DOCUMENTS)} sample documents...")
        result = store.add_documents(SAMPLE_DOCUMENTS)

        logger.info(
            f"Successfully added {result['added']} documents to collection '{result['collection']}'"
        )

        # Verify
        info = store.get_collection_info()
        logger.info(
            f"Collection '{info.name}' now contains {info.count} documents"
        )

        # Close connection
        store.close()
        logger.info("Vector store initialization complete!")

        return 0

    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
