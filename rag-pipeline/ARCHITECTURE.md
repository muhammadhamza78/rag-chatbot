# RAG Pipeline Architecture

Complete technical overview of the RAG data pipeline implementation.

## Project Structure

```
rag-pipeline/
├── config.py              # Configuration management
├── crawler.py             # Website crawling & extraction
├── chunker.py             # Document chunking logic
├── embedder.py            # Cohere embedding generation
├── vector_store.py        # Qdrant vector database operations
├── ingest.py              # Main ingestion orchestration
├── search.py              # Search testing utility
├── check_setup.py         # Setup verification script
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── .gitignore            # Git ignore rules
├── README.md             # Full documentation
├── QUICKSTART.md         # Quick start guide
└── ARCHITECTURE.md       # This file
```

## Data Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        INGESTION PIPELINE                        │
└─────────────────────────────────────────────────────────────────┘

1. CRAWLING (crawler.py)
   ├─ Input: Base URL + Docs paths
   ├─ Process:
   │  ├─ HTTP requests to fetch HTML
   │  ├─ BeautifulSoup parsing
   │  ├─ Filter navigation/UI elements
   │  └─ Extract clean content
   └─ Output: List of documents with metadata

2. CHUNKING (chunker.py)
   ├─ Input: Documents with raw text
   ├─ Process:
   │  ├─ Parse heading structure (H1-H6)
   │  ├─ Split by sections
   │  ├─ Size-based chunking (~800 words)
   │  └─ Add overlap (100 words)
   └─ Output: Chunks with metadata

3. EMBEDDING (embedder.py)
   ├─ Input: Text chunks
   ├─ Process:
   │  ├─ Batch chunks (96 per call)
   │  ├─ Call Cohere embed API
   │  └─ Handle errors & retries
   └─ Output: Chunks with embeddings

4. STORAGE (vector_store.py)
   ├─ Input: Chunks with embeddings
   ├─ Process:
   │  ├─ Create/connect to collection
   │  ├─ Prepare point structures
   │  └─ Batch upload to Qdrant
   └─ Output: Indexed vectors in Qdrant

┌─────────────────────────────────────────────────────────────────┐
│                         SEARCH PIPELINE                          │
└─────────────────────────────────────────────────────────────────┘

1. QUERY EMBEDDING
   ├─ Input: Query text
   ├─ Process: Cohere embed (input_type=search_query)
   └─ Output: Query vector

2. VECTOR SEARCH
   ├─ Input: Query vector + filters
   ├─ Process: Qdrant cosine similarity search
   └─ Output: Top-K similar chunks with scores
```

## Module Details

### 1. config.py

**Purpose**: Centralized configuration management

**Key Functions**:
- Load environment variables from `.env`
- Validate required settings
- Provide defaults for optional settings

**Configuration Variables**:
- `COHERE_API_KEY`: veJvc2o57QNxJQ0wOvYzTMBFx6dBRMEfBwI4hySv
- `QDRANT_URL`: https://f439d63a-a0ed-4da2-bcf6-043ed56adcf8.europe-west3-0.gcp.cloud.qdrant.io
- `QDRANT_API_KEY`: f439d63a-a0ed-4da2-bcf6-043ed56adcf8
- `QDRANT_COLLECTION_NAME`: my-embedded
- `WEBSITE_BASE_URL`: http://localhost:3000
- `CHUNK_SIZE`: 800 (default: 800)
- `CHUNK_OVERLAP`: 100s (default: 100)
- `EMBEDDING_MODEL`: embed-english-v3.0
- `DOCS_PATHS`: List of documentation paths to crawl

---

### 2. crawler.py

**Purpose**: Extract clean content from Docusaurus website

**Class**: `DocusaurusCrawler`

**Key Methods**:
- `extract_page_content(url)`: Fetch and parse a single page
- `_extract_title(soup)`: Extract page title from HTML
- `_extract_main_content(soup)`: Extract article content, filter UI elements
- `_extract_module_from_url(url)`: Parse module name from URL
- `crawl_docs_path(path)`: Crawl a docs section and linked pages
- `crawl_all_docs(paths)`: Crawl multiple documentation paths

**Extraction Strategy**:
1. Target Docusaurus-specific selectors (`article`, `.markdown`, etc.)
2. Remove unwanted elements (nav, footer, sidebar, TOC)
3. Extract clean text with newline separation
4. Preserve heading structure

**Output Format**:
```python
{
    'url': 'https://...',
    'title': 'Page Title',
    'content': 'Clean text content...',
    'module': 'module-01'
}
```

---

### 3. chunker.py

**Purpose**: Split documents into semantically meaningful chunks

**Class**: `TextChunker`

**Key Methods**:
- `chunk_document(document)`: Chunk a single document
- `_split_by_headings(text)`: Parse heading hierarchy
- `_chunk_section(text, headings, ...)`: Size-based chunking with overlap
- `chunk_all_documents(documents)`: Batch process documents

**Chunking Strategy**:

1. **Heading-based splitting**:
   - Parse markdown headings (`#`, `##`, `###`)
   - Maintain heading hierarchy stack
   - Split at heading boundaries

2. **Size-based chunking**:
   - Target: 800 words per chunk
   - Overlap: 100 words between chunks
   - Prevents splitting mid-section when possible

3. **Metadata enrichment**:
   - Add heading hierarchy breadcrumb
   - Add chunk position (index/total)
   - Generate unique chunk ID

**Output Format**:
```python
{
    'text': 'Chunk content...',
    'url': 'https://...',
    'title': 'Page Title',
    'module': 'module-01',
    'heading_hierarchy': 'Chapter > Section > Subsection',
    'chunk_index': 0,
    'total_chunks': 3,
    'chunk_id': 'abc123_0'
}
```

---

### 4. embedder.py

**Purpose**: Generate embeddings using Cohere API

**Class**: `CohereEmbedder`

**Key Methods**:
- `embed_chunks(chunks)`: Batch embed multiple chunks
- `embed_query(query)`: Embed a search query
- `get_embedding_dimension()`: Get model dimension

**Embedding Strategy**:

1. **Batch processing**:
   - Batch size: 96 (Cohere max)
   - Rate limiting: 0.5s between batches
   - Error handling: Skip failed batches

2. **Model settings**:
   - Model: `embed-english-v3.0` (1024 dims)
   - Input type: `search_document` for indexing
   - Input type: `search_query` for queries

**API Call**:
```python
response = client.embed(
    texts=[...],
    model="embed-english-v3.0",
    input_type="search_document"
)
```

---

### 5. vector_store.py

**Purpose**: Manage Qdrant vector database operations

**Class**: `QdrantVectorStore`

**Key Methods**:
- `create_collection(recreate)`: Initialize collection
- `insert_chunks(chunks)`: Upload vectors
- `search(query_vector, limit, filter)`: Vector similarity search
- `get_collection_info()`: Get stats

**Collection Configuration**:
- **Distance metric**: Cosine similarity
- **Vector size**: 1024 (for embed-english-v3.0)
- **Batch upload**: 100 points per batch

**Search Parameters**:
- **Limit**: Top-K results to return
- **Filter**: Optional metadata filters (e.g., module)
- **Query filter**: Qdrant Filter object

**Point Structure**:
```python
PointStruct(
    id=uuid.uuid4(),
    vector=[...],  # 1024-dim embedding
    payload={      # Metadata
        'text': '...',
        'url': '...',
        'title': '...',
        'module': '...',
        'heading_hierarchy': '...',
        'chunk_index': 0,
        'total_chunks': 3,
        'chunk_id': '...'
    }
)
```

---

### 6. ingest.py

**Purpose**: Orchestrate the complete ingestion pipeline

**Main Function**: `run_ingestion_pipeline()`

**Pipeline Stages**:
1. Initialize crawler
2. Crawl all documentation paths
3. Initialize chunker
4. Chunk all documents
5. Initialize embedder
6. Generate embeddings
7. Initialize vector store
8. Create collection (if needed)
9. Upload chunks

**CLI Options**:
- `--base-url`: Override config URL
- `--recreate-collection`: Delete and recreate
- `--no-save-intermediate`: Skip JSON output

**Output**:
- `output/1_documents.json`: Extracted documents
- `output/2_chunks.json`: Chunked data
- Console logs with progress

---

### 7. search.py

**Purpose**: Test vector search functionality

**Main Function**: `search_query()`

**Features**:
- Single query search
- Batch sample queries
- Module filtering
- Configurable result limit
- Formatted output display

**CLI Usage**:
```bash
# Single query
python search.py "What is physical AI?"

# Sample queries
python search.py --sample-queries

# With filters
python search.py "sensors" --module module-01 --limit 10
```

---

## Metadata Schema

Each vector in Qdrant carries rich metadata:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `text` | string | Chunk content | "Physical AI combines..." |
| `url` | string | Source page URL | "https://site.com/docs/..." |
| `title` | string | Page title | "Understanding Physical AI" |
| `module` | string | Module identifier | "module-01" |
| `heading_hierarchy` | string | Breadcrumb trail | "Chapter 1 > Intro > Concepts" |
| `chunk_index` | int | Position in document | 0 |
| `total_chunks` | int | Total chunks from page | 5 |
| `chunk_id` | string | Unique identifier | "abc123_0" |

## Performance Characteristics

### Crawling
- **Rate**: ~2-3 seconds per page
- **Bottleneck**: HTTP requests
- **Optimization**: Can parallelize, but be respectful

### Chunking
- **Rate**: Near-instantaneous
- **Bottleneck**: None
- **Optimization**: Already efficient

### Embedding
- **Rate**: ~1-2 seconds per batch (96 chunks)
- **Bottleneck**: API calls
- **Optimization**: Maximize batch size, parallelize carefully

### Storage
- **Rate**: ~0.5 seconds per batch (100 points)
- **Bottleneck**: Network/API
- **Optimization**: Already batched

### Typical Metrics (50-page site)
- Total pages: ~50
- Total chunks: ~200-500
- Embedding time: ~3-5 minutes
- Total time: ~5-10 minutes

## Error Handling

### Crawler
- HTTP errors: Log and skip page
- Parsing errors: Log and return None
- Empty content: Log warning

### Embedder
- API errors: Skip batch, continue
- Invalid responses: Filter out
- Rate limiting: Built-in delays

### Vector Store
- Connection errors: Raise exception
- Upload errors: Log batch, continue
- Collection exists: Handle gracefully

## Extensibility

### Adding New Data Sources
1. Implement new crawler class
2. Return documents in same format
3. Use existing chunker/embedder/storage

### Changing Chunking Strategy
1. Modify `TextChunker` class
2. Maintain output format
3. Adjust `CHUNK_SIZE` config

### Using Different Embeddings
1. Implement new embedder class
2. Update `config.py`
3. Ensure dimension matches

### Alternative Vector Stores
1. Implement new store class
2. Match interface (create, insert, search)
3. Update `config.py`

## Best Practices

1. **Always run `check_setup.py` first**
2. **Use `--recreate-collection` on first run**
3. **Review intermediate JSON files**
4. **Test search before integrating**
5. **Monitor API usage and costs**
6. **Back up collection before major changes**

## Security Considerations

1. **Never commit `.env` file**
2. **Use read-only API keys when possible**
3. **Validate user input in search queries**
4. **Rate limit search endpoints**
5. **Monitor API key usage**

## Future Enhancements

Potential improvements:

- [ ] Incremental updates (only new/changed pages)
- [ ] Multimodal support (images, diagrams)
- [ ] Hybrid search (keyword + vector)
- [ ] Reranking with Cohere Rerank
- [ ] Caching layer for frequent queries
- [ ] Monitoring and observability
- [ ] A/B testing different chunking strategies
- [ ] Automated evaluation metrics
