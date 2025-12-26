"""
Main ingestion script for RAG pipeline.
Orchestrates crawling, chunking, embedding, and storage.
"""

import logging
from typing import Optional
import json
from pathlib import Path

from crawler import DocusaurusCrawler
from chunker import TextChunker
from embedder import CohereEmbedder
from vector_store import QdrantVectorStore
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def save_intermediate_data(data: list, filename: str):
    """Save intermediate data to JSON for debugging/inspection."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    filepath = output_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved intermediate data to {filepath}")


def run_ingestion_pipeline(
    base_url: Optional[str] = None,
    docs_paths: Optional[list] = None,
    save_intermediate: bool = True,
    recreate_collection: bool = False
):
    """
    Run the complete ingestion pipeline.

    Args:
        base_url: Override base URL from config
        docs_paths: Override docs paths from config
        save_intermediate: Save intermediate data for debugging
        recreate_collection: Recreate Qdrant collection (deletes existing data)
    """
    logger.info("=" * 80)
    logger.info("Starting RAG Ingestion Pipeline")
    logger.info("=" * 80)

    # Use config values or overrides
    base_url = base_url or config.WEBSITE_BASE_URL
    docs_paths = docs_paths or config.DOCS_PATHS

    logger.info(f"Base URL: {base_url}")
    logger.info(f"Docs paths: {docs_paths}")

    # Step 1: Crawl website
    logger.info("\n[Step 1/5] Crawling website...")
    crawler = DocusaurusCrawler(base_url=base_url)
    documents = crawler.crawl_all_docs(docs_paths)

    if not documents:
        logger.error("No documents extracted. Check base URL and docs paths.")
        return

    logger.info(f"Extracted {len(documents)} documents")

    if save_intermediate:
        save_intermediate_data(documents, "1_documents.json")

    # Step 2: Chunk documents
    logger.info("\n[Step 2/5] Chunking documents...")
    chunker = TextChunker(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    chunks = chunker.chunk_all_documents(documents)

    if not chunks:
        logger.error("No chunks created. Check chunking configuration.")
        return

    logger.info(f"Created {len(chunks)} chunks")

    if save_intermediate:
        # Save without embeddings
        chunks_preview = [{k: v for k, v in c.items() if k != 'embedding'} for c in chunks]
        save_intermediate_data(chunks_preview, "2_chunks.json")

    # Step 3: Generate embeddings
    logger.info("\n[Step 3/5] Generating embeddings...")
    embedder = CohereEmbedder(
        api_key=config.COHERE_API_KEY,
        model=config.EMBEDDING_MODEL,
        input_type=config.EMBEDDING_INPUT_TYPE
    )
    chunks_with_embeddings = embedder.embed_chunks(chunks)

    if not chunks_with_embeddings:
        logger.error("No embeddings generated. Check Cohere API key and configuration.")
        return

    logger.info(f"Generated embeddings for {len(chunks_with_embeddings)} chunks")

    # Step 4: Create/connect to vector store
    logger.info("\n[Step 4/5] Setting up vector store...")
    embedding_dim = embedder.get_embedding_dimension()
    vector_store = QdrantVectorStore(
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_KEY,
        collection_name=config.QDRANT_COLLECTION_NAME,
        embedding_dimension=embedding_dim
    )

    vector_store.create_collection(recreate=recreate_collection)

    # Step 5: Insert into vector store
    logger.info("\n[Step 5/5] Inserting into vector store...")
    vector_store.insert_chunks(chunks_with_embeddings)

    # Get collection info
    collection_info = vector_store.get_collection_info()
    logger.info(f"\nCollection info: {collection_info}")

    logger.info("\n" + "=" * 80)
    logger.info("Ingestion pipeline completed successfully!")
    logger.info("=" * 80)
    logger.info(f"Total documents: {len(documents)}")
    logger.info(f"Total chunks: {len(chunks_with_embeddings)}")
    logger.info(f"Collection: {config.QDRANT_COLLECTION_NAME}")
    logger.info(f"Points in collection: {collection_info.get('points_count', 'N/A')}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run RAG ingestion pipeline for Physical AI book"
    )
    parser.add_argument(
        "--base-url",
        help="Override base URL from config",
        default=None
    )
    parser.add_argument(
        "--recreate-collection",
        action="store_true",
        help="Recreate Qdrant collection (WARNING: deletes existing data)"
    )
    parser.add_argument(
        "--no-save-intermediate",
        action="store_true",
        help="Don't save intermediate data files"
    )

    args = parser.parse_args()

    try:
        run_ingestion_pipeline(
            base_url=args.base_url,
            save_intermediate=not args.no_save_intermediate,
            recreate_collection=args.recreate_collection
        )
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        exit(1)
