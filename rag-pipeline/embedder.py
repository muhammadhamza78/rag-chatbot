"""
Embedding generation module using Cohere's embedding models.
Handles batching and error handling for reliable embedding generation.
"""

import cohere
from typing import List, Dict
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CohereEmbedder:
    """Wrapper for Cohere embedding generation."""

    def __init__(
        self,
        api_key: str,
        model: str = "embed-english-v3.0",
        input_type: str = "search_document",
        batch_size: int = 96  # Cohere's max batch size
    ):
        """
        Initialize the embedder.

        Args:
            api_key: Cohere API key
            model: Cohere embedding model name
            input_type: Type of embedding (search_document or search_query)
            batch_size: Number of texts to embed in a single API call
        """
        self.client = cohere.Client(api_key)
        self.model = model
        self.input_type = input_type
        self.batch_size = batch_size

    def embed_chunks(self, chunks: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Generate embeddings for text chunks.

        Args:
            chunks: List of chunk dictionaries with 'text' field

        Returns:
            List of chunks with added 'embedding' field
        """
        total_chunks = len(chunks)
        logger.info(f"Generating embeddings for {total_chunks} chunks...")

        # Process in batches
        for i in range(0, total_chunks, self.batch_size):
            batch = chunks[i:i + self.batch_size]
            batch_texts = [chunk['text'] for chunk in batch]

            try:
                logger.info(f"Processing batch {i // self.batch_size + 1}/{(total_chunks + self.batch_size - 1) // self.batch_size}")

                # Generate embeddings
                response = self.client.embed(
                    texts=batch_texts,
                    model=self.model,
                    input_type=self.input_type
                )

                # Add embeddings to chunks
                for chunk, embedding in zip(batch, response.embeddings):
                    chunk['embedding'] = embedding

                # Be nice to the API
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error generating embeddings for batch starting at {i}: {e}")
                # Add None for failed embeddings
                for chunk in batch:
                    if 'embedding' not in chunk:
                        chunk['embedding'] = None

        # Filter out chunks with failed embeddings
        valid_chunks = [c for c in chunks if c.get('embedding') is not None]
        failed_count = total_chunks - len(valid_chunks)

        if failed_count > 0:
            logger.warning(f"Failed to generate embeddings for {failed_count} chunks")

        logger.info(f"Successfully generated embeddings for {len(valid_chunks)} chunks")
        return valid_chunks

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.

        Args:
            query: Search query text

        Returns:
            Embedding vector
        """
        try:
            response = self.client.embed(
                texts=[query],
                model=self.model,
                input_type="search_query"
            )
            return response.embeddings[0]
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings for this model.

        Returns:
            Embedding dimension
        """
        # embed-english-v3.0 produces 1024-dimensional embeddings
        if "v3.0" in self.model:
            return 1024
        # embed-english-light-v3.0 produces 384-dimensional embeddings
        elif "light-v3.0" in self.model:
            return 384
        else:
            # Default, or query the API with a test embedding
            test_response = self.client.embed(
                texts=["test"],
                model=self.model,
                input_type=self.input_type
            )
            return len(test_response.embeddings[0])
