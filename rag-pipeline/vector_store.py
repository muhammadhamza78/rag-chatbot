"""
Vector storage module using Qdrant.
Handles collection creation, data insertion, and vector search.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)
from typing import List, Dict, Optional
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """Wrapper for Qdrant vector database operations."""

    def __init__(
        self,
        url: str,
        api_key: str,
        collection_name: str,
        embedding_dimension: int = 1024
    ):
        """
        Initialize the vector store.

        Args:
            url: Qdrant cluster URL
            api_key: Qdrant API key
            collection_name: Name of the collection to use
            embedding_dimension: Dimension of embedding vectors
        """
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name
        self.embedding_dimension = embedding_dimension

    def create_collection(self, recreate: bool = False):
        """
        Create a collection for storing embeddings.

        Args:
            recreate: If True, delete existing collection and create new one
        """
        # Check if collection exists
        collections = self.client.get_collections().collections
        collection_exists = any(c.name == self.collection_name for c in collections)

        if collection_exists:
            if recreate:
                logger.info(f"Deleting existing collection: {self.collection_name}")
                self.client.delete_collection(self.collection_name)
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                return

        # Create collection
        logger.info(f"Creating collection: {self.collection_name}")
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.embedding_dimension,
                distance=Distance.COSINE
            )
        )
        logger.info(f"Collection {self.collection_name} created successfully")

    def insert_chunks(self, chunks: List[Dict[str, any]], batch_size: int = 100):
        """
        Insert chunks with embeddings into the vector store.

        Args:
            chunks: List of chunks with 'embedding' and metadata fields
            batch_size: Number of points to upload in a single batch
        """
        total_chunks = len(chunks)
        logger.info(f"Inserting {total_chunks} chunks into {self.collection_name}...")

        points = []
        for chunk in chunks:
            # Validate chunk has embedding
            if 'embedding' not in chunk or chunk['embedding'] is None:
                logger.warning(f"Skipping chunk without embedding: {chunk.get('chunk_id')}")
                continue

            # Prepare metadata (exclude embedding and text for payload)
            payload = {
                'text': chunk['text'],
                'url': chunk['url'],
                'title': chunk['title'],
                'module': chunk.get('module'),
                'heading_hierarchy': chunk.get('heading_hierarchy'),
                'chunk_index': chunk.get('chunk_index'),
                'total_chunks': chunk.get('total_chunks'),
                'chunk_id': chunk.get('chunk_id'),
            }

            # Create point
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=chunk['embedding'],
                payload=payload
            )
            points.append(point)

        # Upload in batches
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            logger.info(f"Uploading batch {i // batch_size + 1}/{(len(points) + batch_size - 1) // batch_size}")

            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
            except Exception as e:
                logger.error(f"Error uploading batch starting at {i}: {e}")

        logger.info(f"Successfully inserted {len(points)} chunks into vector store")

    def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        module_filter: Optional[str] = None
    ) -> List[Dict[str, any]]:
        """
        Search for similar chunks.

        Args:
            query_vector: Query embedding vector
            limit: Number of results to return
            module_filter: Optional module name to filter results

        Returns:
            List of search results with text, metadata, and score
        """
        # Build filter if needed
        query_filter = None
        if module_filter:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="module",
                        match=MatchValue(value=module_filter)
                    )
                ]
            )

        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=query_filter
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'text': result.payload.get('text'),
                    'url': result.payload.get('url'),
                    'title': result.payload.get('title'),
                    'module': result.payload.get('module'),
                    'heading_hierarchy': result.payload.get('heading_hierarchy'),
                    'score': result.score,
                    'chunk_id': result.payload.get('chunk_id'),
                })

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise

    def get_collection_info(self) -> Dict[str, any]:
        """
        Get information about the collection.

        Returns:
            Dictionary with collection stats
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                'name': collection_info.name,
                'points_count': collection_info.points_count,
                'vectors_count': collection_info.vectors_count,
                'status': collection_info.status,
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}
