# RAG Pipeline for Physical AI Book

A production-ready RAG (Retrieval-Augmented Generation) data pipeline for ingesting the Physical AI Docusaurus website, generating embeddings, and storing them in a vector database.

## Overview

This pipeline:
1. **Crawls** the deployed Docusaurus website and extracts clean content
2. **Chunks** documents into semantically meaningful pieces with overlap
3. **Generates embeddings** using Cohere's latest embedding models
4. **Stores** embeddings with rich metadata in Qdrant Cloud
5. **Enables** vector search for relevant content retrieval

## Features

- **Intelligent Crawling**: Docusaurus-aware content extraction that filters navigation, sidebars, and UI elements
- **Semantic Chunking**: Heading-based chunking that preserves document structure
- **Rich Metadata**: Each chunk includes URL, title, module, heading hierarchy, and position info
- **Batch Processing**: Efficient batching for API calls with error handling
- **Configurable**: All settings managed via environment variables
- **Debuggable**: Saves intermediate data at each pipeline stage

## Prerequisites

- Python 3.8+
- Cohere API key (get one at [cohere.com](https://cohere.com))
- Qdrant Cloud account (free tier available at [qdrant.io](https://qdrant.io))

## Installation

1. **Clone or navigate to the pipeline directory**:
   ```bash
   cd rag-pipeline
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your API keys
   ```

## Configuration

Edit the `.env` file with your credentials and settings:

```env
# Cohere API Configuration
COHERE_API_KEY=your_cohere_api_key_here

# Qdrant Configuration
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=physical_ai_book

# Website Configuration
WEBSITE_BASE_URL=https://your-deployed-site.vercel.app

# Chunking Configuration
CHUNK_SIZE=800
CHUNK_OVERLAP=100

# Embedding Configuration
EMBEDDING_MODEL=embed-english-v3.0
EMBEDDING_INPUT_TYPE=search_document
```

### Configuration Details

- **CHUNK_SIZE**: Target chunk size in words (default: 800)
- **CHUNK_OVERLAP**: Word overlap between chunks for context preservation (default: 100)
- **EMBEDDING_MODEL**: Cohere embedding model (recommended: `embed-english-v3.0`)
- **EMBEDDING_INPUT_TYPE**: `search_document` for indexing, `search_query` for queries

## Usage

### 1. Run the Ingestion Pipeline

Ingest the entire website into your vector database:

```bash
python ingest.py
```

**Options**:
- `--base-url URL`: Override the base URL from config
- `--recreate-collection`: Delete and recreate the Qdrant collection (⚠️ deletes existing data)
- `--no-save-intermediate`: Skip saving intermediate JSON files

**Example**:
```bash
# First run - create collection and ingest
python ingest.py --recreate-collection

# Update with new content (adds to existing collection)
python ingest.py

# Use a different deployment
python ingest.py --base-url https://staging-site.vercel.app
```

### 2. Test Vector Search

Search the vector store with sample queries:

```bash
# Run predefined sample queries
python search.py --sample-queries

# Search with a custom query
python search.py "What is physical AI?"

# Get more results
python search.py "How do sensors work?" --limit 10

# Filter by module
python search.py "digital twins" --module module-02
```

## Pipeline Architecture

### Data Flow

```
Website → Crawler → Documents → Chunker → Chunks → Embedder → Embeddings → Qdrant
```

### Modules

1. **`config.py`**: Configuration management from environment variables
2. **`crawler.py`**: Website crawling and content extraction
3. **`chunker.py`**: Document chunking with heading-based segmentation
4. **`embedder.py`**: Cohere embedding generation with batching
5. **`vector_store.py`**: Qdrant vector database operations
6. **`ingest.py`**: Main ingestion pipeline orchestration
7. **`search.py`**: Vector search testing utility

### Chunking Strategy

The chunker uses a hybrid approach:

1. **Heading-based segmentation**: Splits documents at heading boundaries (H1, H2, H3)
2. **Size-based chunking**: Breaks large sections into ~800-word chunks
3. **Overlap**: Maintains 100-word overlap between chunks for context
4. **Metadata preservation**: Each chunk includes:
   - Full URL and page title
   - Module name
   - Heading hierarchy (breadcrumb trail)
   - Chunk position (index/total)
   - Unique chunk ID

### Metadata Schema

Each vector in Qdrant has the following payload:

```json
{
  "text": "Chunk text content...",
  "url": "https://site.com/docs/module-01/chapter-01",
  "title": "Understanding Physical AI",
  "module": "module-01",
  "heading_hierarchy": "Chapter 1 > Introduction > Core Concepts",
  "chunk_index": 0,
  "total_chunks": 5,
  "chunk_id": "a1b2c3d4_0"
}
```

## Output

The pipeline creates an `output/` directory with intermediate data:

- `1_documents.json`: Raw extracted documents
- `2_chunks.json`: Chunked documents with metadata

These files are useful for debugging and understanding the pipeline's behavior.

## Testing

### Verify the Ingestion

After running the pipeline, check:

1. **Console output**: Shows progress and final statistics
2. **Qdrant dashboard**: Verify collection creation and point count
3. **Search script**: Test retrieval with sample queries

```bash
python search.py --sample-queries
```

Expected output should show relevant chunks with similarity scores.

## Troubleshooting

### Common Issues

**1. No content extracted**
- Check that `WEBSITE_BASE_URL` is accessible
- Verify the site is deployed and public
- Try accessing the URL in a browser

**2. Cohere API errors**
- Verify your `COHERE_API_KEY` is valid
- Check API rate limits
- Ensure you're using a supported model

**3. Qdrant connection errors**
- Confirm `QDRANT_URL` and `QDRANT_API_KEY` are correct
- Check if your Qdrant cluster is active
- Verify network connectivity

**4. Empty search results**
- Ensure ingestion completed successfully
- Check collection exists in Qdrant dashboard
- Verify `QDRANT_COLLECTION_NAME` matches

### Debug Mode

Enable detailed logging:

```python
# Add to top of ingest.py or search.py
logging.basicConfig(level=logging.DEBUG)
```

## Performance

Typical ingestion metrics:

- **Crawling**: ~2-3 seconds per page
- **Chunking**: Near-instantaneous
- **Embedding**: ~1-2 seconds per batch (96 chunks)
- **Upload**: ~0.5 seconds per batch (100 points)

For a 50-page documentation site:
- **Total time**: ~5-10 minutes
- **Chunks generated**: ~200-500
- **API calls**: ~10-15

## Retrieval and Validation

### Overview

The `retrieve.py` script provides retrieval testing and validation for the RAG pipeline. It queries the Qdrant vector database and validates that retrieval works correctly.

### Quick Test

Test retrieval with a single query:

```bash
python retrieve.py --query "What is physical AI?"
```

### Validation Suite

Run comprehensive validation with 8 test queries:

```bash
python retrieve.py --validate
# or simply
python retrieve.py
```

This tests:
- Definitional queries ("What is X?")
- Procedural queries ("How to X?")
- Conceptual queries ("Explain X")
- Technical queries (short terms, acronyms)
- Cross-module queries
- Comparative queries

**Expected**: ≥75% pass rate (6+ queries passing)

### Interactive Mode

Query multiple times in one session:

```bash
python retrieve.py --interactive
```

Then enter queries one at a time. Type `exit` to quit.

### Module Filtering

Filter results to a specific module:

```bash
python retrieve.py --query "sensors" --module module-01
```

### Custom Result Count

Specify number of results to return:

```bash
python retrieve.py --query "digital twins" --top-k 10
```

### Expected Output

**Validation Suite**:
```
[Q001] What is physical AI?
Type: definitional
✓ PASSED
Top Result:
  Score: 0.8456
  Title: Understanding Physical AI
  Module: module-01

...

VALIDATION SUMMARY
Total Queries: 8
Passed: 7
Failed: 1
Pass Rate: 87.5%
```

**Single Query**:
```
QUERY: What is physical AI?
Total Time: 0.54s
Results: 5

[1] Score: 0.8456
    Title: Understanding Physical AI
    URL: https://site.com/docs/module-01/chapter-01
    Module: module-01
    Section: Chapter 1 > Introduction

    Text:
    Physical AI combines artificial intelligence with physical
    systems to create intelligent machines...

Metadata Validation:
  Passed: 5/5

Content Quality Validation:
  Clean: 5/5
```

### Troubleshooting

**No results found**:
- Query may be too specific - try broader terms
- Check module filter isn't too restrictive
- Verify collection has embeddings: `python check_setup.py`

**Low scores**:
- Expected for very short queries (1-2 words)
- Try longer, more specific queries

**Connection errors**:
- Verify `.env` file configured
- Check Qdrant cluster is running
- Run `python check_setup.py` first

---

## Next Steps

This pipeline provides the data foundation for RAG. To build the complete system:

1. **Retrieval logic**: Use `retrieve.py` for testing, integrate into your app
2. **Reranking**: Add Cohere Rerank for better relevance
3. **LLM integration**: Combine retrieved chunks with Claude/GPT for answers
4. **API layer**: Wrap search in FastAPI or Flask
5. **Frontend**: Build a chat interface

## License

MIT License - see LICENSE file for details

## Contributing

This is an educational project. Feel free to adapt and extend for your needs.
