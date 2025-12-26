"""
Search script for testing vector search functionality.
Tests the ingested data with sample queries.
"""

import logging
from typing import Optional

from embedder import CohereEmbedder
from vector_store import QdrantVectorStore
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def search_query(
    query: str,
    limit: int = 5,
    module_filter: Optional[str] = None,
    verbose: bool = True
):
    """
    Search for relevant chunks given a query.

    Args:
        query: Search query text
        limit: Number of results to return
        module_filter: Optional module filter (e.g., "module-01")
        verbose: Print detailed results
    """
    logger.info(f"Searching for: '{query}'")

    # Initialize embedder
    embedder = CohereEmbedder(
        api_key=config.COHERE_API_KEY,
        model=config.EMBEDDING_MODEL,
    )

    # Generate query embedding
    logger.info("Generating query embedding...")
    query_vector = embedder.embed_query(query)

    # Initialize vector store
    embedding_dim = embedder.get_embedding_dimension()
    vector_store = QdrantVectorStore(
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_KEY,
        collection_name=config.QDRANT_COLLECTION_NAME,
        embedding_dimension=embedding_dim
    )

    # Search
    logger.info("Searching vector store...")
    results = vector_store.search(
        query_vector=query_vector,
        limit=limit,
        module_filter=module_filter
    )

    # Display results
    print("\n" + "=" * 80)
    print(f"SEARCH RESULTS FOR: '{query}'")
    if module_filter:
        print(f"Filtered by module: {module_filter}")
    print("=" * 80)

    if not results:
        print("\nNo results found.")
        return results

    for i, result in enumerate(results, 1):
        print(f"\n[Result {i}] Score: {result['score']:.4f}")
        print(f"Title: {result['title']}")
        print(f"URL: {result['url']}")
        if result.get('module'):
            print(f"Module: {result['module']}")
        if result.get('heading_hierarchy'):
            print(f"Section: {result['heading_hierarchy']}")

        if verbose:
            # Show first 300 characters of text
            text_preview = result['text'][:300]
            if len(result['text']) > 300:
                text_preview += "..."
            print(f"\nText preview:\n{text_preview}")
        print("-" * 80)

    return results


def run_sample_queries():
    """Run a set of sample queries to test the system."""
    sample_queries = [
        "What is physical AI?",
        "How do sensors work in robotics?",
        "Explain digital twins",
        "What is Gazebo used for?",
        "How to simulate physics in robotics?",
    ]

    print("\n" + "=" * 80)
    print("RUNNING SAMPLE QUERIES")
    print("=" * 80)

    for query in sample_queries:
        try:
            search_query(query, limit=3, verbose=False)
            print("\n")
        except Exception as e:
            logger.error(f"Error searching for '{query}': {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Search the RAG vector store"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Search query (if not provided, runs sample queries)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of results to return (default: 5)"
    )
    parser.add_argument(
        "--module",
        help="Filter by module (e.g., module-01)"
    )
    parser.add_argument(
        "--sample-queries",
        action="store_true",
        help="Run sample queries instead of a single query"
    )

    args = parser.parse_args()

    try:
        if args.sample_queries or not args.query:
            run_sample_queries()
        else:
            search_query(
                query=args.query,
                limit=args.limit,
                module_filter=args.module
            )
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        exit(1)
