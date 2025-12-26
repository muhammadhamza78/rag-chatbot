"""
Configuration management for RAG pipeline.
Loads settings from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Cohere Configuration
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY is required. Please set it in .env file")

# Qdrant Configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "physical_ai_book")

if not QDRANT_URL or not QDRANT_API_KEY:
    raise ValueError("QDRANT_URL and QDRANT_API_KEY are required. Please set them in .env file")

# Website Configuration
WEBSITE_BASE_URL = os.getenv("WEBSITE_BASE_URL", "http://localhost:3000")

# Chunking Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# Embedding Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "embed-english-v3.0")
EMBEDDING_INPUT_TYPE = os.getenv("EMBEDDING_INPUT_TYPE", "search_document")

# Docusaurus paths to crawl
DOCS_PATHS = [
    "/docs/intro",
    "/docs/module-01",
    "/docs/module-02",
    "/docs/module-03",
    "/docs/module-04",
    "/docs/glossary",
]
