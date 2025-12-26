# RAG Pipeline Implementation Plan

**Objective**: Extract content from deployed Docusaurus website, generate embeddings using Cohere, and store in Qdrant for RAG chatbot retrieval.

**Target**: Backend engineers building the data ingestion foundation for a RAG system.

---

## 1. URL Discovery and Crawling Strategy

### 1.1 URL Discovery Approach

**Strategy**: Seed-based crawling with link following

**Implementation**:
- Start with predefined seed URLs (documentation entry points)
- Extract links from each page
- Follow only same-domain links within `/docs/` paths
- Track visited URLs to prevent duplicates

**Seed URLs**:
```python
DOCS_PATHS = [
    "/docs/intro",
    "/docs/module-01",
    "/docs/module-02",
    "/docs/module-03",
    "/docs/module-04",
    "/docs/glossary",
]
```

**Rationale**:
- Docusaurus sites have predictable structure
- Seed URLs ensure comprehensive coverage
- Link following captures all connected pages
- Filtering prevents crawling unrelated content (blog, external links)

### 1.2 Crawling Implementation

**HTTP Client**: `requests` library with session management

**Request Strategy**:
- User-Agent: `RAG-Pipeline-Crawler/1.0 (Educational Purpose)`
- Timeout: 30 seconds per request
- Delay: 0.5 seconds between requests (respectful crawling)
- Error handling: Log and skip failed pages, continue pipeline

**Deduplication**:
- Maintain `visited_urls` set
- Normalize URLs (remove query params, fragments)
- Check before fetching to avoid duplicate requests

**Algorithm**:
```
for each seed_path in DOCS_PATHS:
    url = base_url + seed_path
    extract_page(url)

    links = find_all_links(url)
    for link in links:
        if link not in visited and is_docs_path(link):
            extract_page(link)
```

---

## 2. Text Extraction and HTML Cleaning

### 2.1 HTML Parsing

**Parser**: BeautifulSoup with `lxml` backend

**Why lxml**: Faster than html.parser, more lenient than html5lib

### 2.2 Content Extraction Strategy

**Target Elements** (Docusaurus-specific):
```python
content_selectors = [
    'article',                        # Main article wrapper
    'main',                           # HTML5 main element
    '.markdown',                      # Docusaurus markdown class
    '[class*="docMainContainer"]',    # Docusaurus container
    '[class*="docItemContainer"]',    # Docusaurus item wrapper
]
```

**Removal Strategy** (filter unwanted elements):
```python
unwanted_selectors = [
    'nav',                            # Navigation bars
    'header',                         # Page headers
    'footer',                         # Page footers
    '.navbar',                        # Top navbar
    '.sidebar',                       # Sidebar navigation
    '[class*="tableOfContents"]',     # TOC widget
    '[class*="breadcrumb"]',          # Breadcrumbs
    '.pagination-nav',                # Prev/next links
    '.theme-edit-this-page',          # Edit links
    '.theme-last-updated',            # Update timestamps
    'button',                         # Interactive buttons
    'script',                         # JavaScript
    'style',                          # CSS
]
```

**Text Extraction Process**:
1. Parse HTML with BeautifulSoup
2. Find main content container (try selectors in order)
3. Remove unwanted elements
4. Extract text with `get_text(separator='\n', strip=True)`
5. Clean excessive whitespace
6. Return normalized text

**Rationale**:
- Docusaurus has consistent structure across pages
- Targeting specific elements ensures clean content
- Removing UI elements prevents noise in embeddings
- Preserving newlines maintains heading structure

### 2.3 Metadata Extraction

**Extract from each page**:
- **Title**: From `<h1>` or `<title>` tag
- **URL**: Full canonical URL
- **Module**: Parsed from URL path (e.g., `/docs/module-01/...` → "module-01")

**Example**:
```python
{
    'url': 'https://site.com/docs/module-01/chapter-01',
    'title': 'Understanding Physical AI',
    'content': 'Physical AI is...',
    'module': 'module-01'
}
```

---

## 3. Chunking Strategy

### 3.1 Chunking Approach

**Strategy**: Hybrid heading-based + size-based chunking with overlap

**Why Hybrid**:
- Heading-based: Preserves semantic boundaries
- Size-based: Ensures consistent chunk sizes for embeddings
- Overlap: Maintains context across chunk boundaries

### 3.2 Chunking Algorithm

**Step 1: Parse Heading Structure**
```
Parse markdown headings (# H1, ## H2, ### H3)
Build heading hierarchy stack
Split document at heading boundaries
```

**Step 2: Size-Based Chunking**
```
For each section:
    If section <= chunk_size:
        Return as single chunk
    Else:
        Split into overlapping chunks:
            chunk_1: words[0:800]
            chunk_2: words[700:1500]  # 100-word overlap
            chunk_3: words[1400:2200]
            ...
```

**Step 3: Metadata Enrichment**
```
For each chunk:
    Add heading_hierarchy breadcrumb
    Add chunk_index and total_chunks
    Generate unique chunk_id
```

### 3.3 Chunk Size Rationale

**Selected Parameters**:
- **Chunk Size**: 800 words
- **Overlap**: 100 words (12.5%)

**Rationale**:

| Consideration | Decision | Reasoning |
|---------------|----------|-----------|
| Token count | ~1000 tokens | 800 words ≈ 1000 tokens (safe under typical context limits) |
| Semantic coherence | Heading-based | Preserves logical document structure |
| Context preservation | 100-word overlap | Ensures continuity, prevents information loss at boundaries |
| Retrieval granularity | Medium chunks | Balance between specificity and context |
| Embedding quality | Optimal for Cohere | Sufficient context for semantic understanding |

**Alternatives Considered**:

| Approach | Size | Pros | Cons | Decision |
|----------|------|------|------|----------|
| Small chunks | 200-300 words | Precise retrieval | Loss of context | ❌ Rejected |
| Medium chunks | 800 words | Good balance | - | ✅ **Selected** |
| Large chunks | 1500+ words | Maximum context | Noisy retrieval | ❌ Rejected |

### 3.4 Chunk Metadata Schema

**Metadata Fields**:
```python
{
    'text': str,                    # Chunk content
    'url': str,                     # Source page URL
    'title': str,                   # Page title
    'module': str,                  # Module identifier (e.g., "module-01")
    'heading_hierarchy': str,       # Breadcrumb (e.g., "Chapter 1 > Section 1.2")
    'chunk_index': int,             # Position in document (0-indexed)
    'total_chunks': int,            # Total chunks from this document
    'chunk_id': str,                # Unique identifier (hash_8chars + index)
}
```

**Why These Fields**:
- `text`: Required for retrieval and display
- `url`: Source attribution, deep linking
- `title`: Context for relevance ranking
- `module`: Filtering (e.g., "only show module-01 results")
- `heading_hierarchy`: Contextual breadcrumb for user navigation
- `chunk_index/total_chunks`: Reconstruct document order
- `chunk_id`: Unique identifier for deduplication and updates

---

## 4. Embedding Generation Flow

### 4.1 Cohere API Integration

**Model Selection**: `embed-english-v3.0`

**Rationale**:
- Latest stable Cohere model
- 1024-dimensional embeddings (good balance)
- Optimized for retrieval tasks
- Supports `input_type` parameter for better quality

**Configuration**:
```python
model = "embed-english-v3.0"
input_type = "search_document"  # For indexing documents
dimension = 1024
```

### 4.2 Embedding Generation Process

**Batch Processing**:
```
chunks = [...all chunks...]
batch_size = 96  # Cohere max batch size

for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size]
    texts = [chunk['text'] for chunk in batch]

    response = cohere.embed(
        texts=texts,
        model="embed-english-v3.0",
        input_type="search_document"
    )

    for chunk, embedding in zip(batch, response.embeddings):
        chunk['embedding'] = embedding

    sleep(0.5)  # Rate limiting
```

**Error Handling**:
- Try-except around each batch
- Log errors but continue processing
- Mark failed chunks (embedding=None)
- Filter out failed chunks before storage
- Report failure count at end

**Rate Limiting**:
- 0.5 second delay between batches
- Respects Cohere's rate limits
- Prevents API throttling

### 4.3 Query Embedding

**Configuration for Search**:
```python
input_type = "search_query"  # Different from documents!
```

**Why Different**:
- Cohere optimizes embeddings based on input_type
- `search_document`: Optimized for being retrieved
- `search_query`: Optimized for querying
- Results in better semantic matching

**Usage**:
```python
query_embedding = cohere.embed(
    texts=[user_query],
    model="embed-english-v3.0",
    input_type="search_query"
).embeddings[0]
```

---

## 5. Qdrant Collection Schema and Metadata Design

### 5.1 Collection Configuration

**Collection Settings**:
```python
collection_name = "physical_ai_book"
vector_config = {
    'size': 1024,              # Cohere embed-v3.0 dimension
    'distance': Distance.COSINE  # Cosine similarity metric
}
```

**Distance Metric Rationale**:

| Metric | Use Case | Choice |
|--------|----------|--------|
| Cosine | Text similarity, normalized vectors | ✅ **Selected** |
| Dot Product | When magnitude matters | ❌ Not needed |
| Euclidean | Absolute distance | ❌ Less suitable for text |

Cosine similarity is standard for text embeddings because:
- Focuses on direction, not magnitude
- Normalized (0 to 1 scale)
- Well-suited for semantic similarity

### 5.2 Point Structure

**Qdrant Point Schema**:
```python
PointStruct(
    id=str(uuid.uuid4()),        # Random UUID
    vector=[...1024 floats...],   # Cohere embedding
    payload={                     # Metadata
        'text': str,
        'url': str,
        'title': str,
        'module': str,
        'heading_hierarchy': str,
        'chunk_index': int,
        'total_chunks': int,
        'chunk_id': str,
    }
)
```

**ID Strategy**:
- Use random UUIDs (not sequential)
- No need for deterministic IDs (handled by chunk_id in payload)
- Prevents ID collisions

### 5.3 Qdrant Cloud Free Tier Considerations

**Limits**:
- 1 GB storage
- 100,000 vectors max
- Shared resources

**Optimization Strategies**:

| Strategy | Implementation | Impact |
|----------|----------------|--------|
| Batch uploads | 100 points per batch | Reduces API calls |
| Efficient metadata | Store only essential fields | Saves storage |
| Text length | Don't store full documents | Use chunks only |
| Collection reuse | Update vs recreate | Faster iterations |

**Estimated Usage** (50-page site):
- Chunks: ~500
- Vector size: 1024 × 4 bytes = 4KB per vector
- Metadata: ~500 bytes per chunk
- Total: ~2.25 MB (well within 1GB limit)

**Scaling Headroom**: Can handle ~200,000 similar chunks before hitting limits

### 5.4 Search Configuration

**Search Parameters**:
```python
results = qdrant.search(
    collection_name="physical_ai_book",
    query_vector=[...1024 floats...],
    limit=5,                           # Top-K results
    query_filter=Filter(               # Optional filtering
        must=[
            FieldCondition(
                key="module",
                match=MatchValue(value="module-01")
            )
        ]
    )
)
```

**Filter Support**:
- Filter by module (e.g., only module-01)
- Filter by URL pattern
- Combine multiple conditions
- Applied before vector search (efficient)

---

## 6. Error Handling and Idempotency Strategy

### 6.1 Error Handling by Component

**Crawler Errors**:
```python
try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
except requests.RequestException as e:
    logger.error(f"Failed to fetch {url}: {e}")
    return None  # Skip this page, continue with others
```

**Embedding Errors**:
```python
try:
    response = cohere.embed(texts=batch, ...)
except Exception as e:
    logger.error(f"Embedding batch {i} failed: {e}")
    # Mark chunks with embedding=None
    # Continue with next batch
```

**Storage Errors**:
```python
try:
    qdrant.upsert(collection_name, points=batch)
except Exception as e:
    logger.error(f"Upload batch {i} failed: {e}")
    # Continue with next batch
```

**Philosophy**:
- Fail gracefully on individual items
- Continue processing pipeline
- Log all errors
- Report summary statistics at end

### 6.2 Idempotency Strategy

**Collection Management**:
```python
# Option 1: Create if not exists (idempotent)
if not collection_exists(name):
    create_collection(name)

# Option 2: Recreate (non-idempotent, use with flag)
if recreate_flag:
    delete_collection(name)
create_collection(name)
```

**Upload Strategy**:
```python
# Use upsert (not insert)
qdrant.upsert(...)  # Updates existing, inserts new
```

**Why Upsert**:
- Running pipeline twice won't duplicate data
- Can update existing embeddings
- Handles partial failures gracefully

**Chunk ID Strategy**:
```python
chunk_id = f"{url_hash}_{chunk_index}"
```

**Benefits**:
- Deterministic chunk IDs
- Same URL + index = same chunk_id
- Enables deduplication
- Allows incremental updates

### 6.3 Validation and Rollback

**Pre-Flight Validation**:
```python
# Before running pipeline
assert COHERE_API_KEY is not None
assert QDRANT_URL is not None
assert website_is_accessible(BASE_URL)
```

**Progress Checkpoints**:
```python
# Save intermediate data
save_json(documents, "output/1_documents.json")
save_json(chunks, "output/2_chunks.json")
# Don't save embeddings (too large)
```

**Post-Ingestion Validation**:
```python
# After upload
collection_info = qdrant.get_collection(name)
assert collection_info.points_count > 0
logger.info(f"Uploaded {collection_info.points_count} points")

# Test search
results = search("test query", limit=1)
assert len(results) > 0
```

**Rollback Strategy**:
- Keep previous collection (use versioned names)
- Test new collection before switching
- Can delete and recreate if needed

---

## 7. Configuration via Environment Variables

### 7.1 Configuration Schema

**Environment Variables**:

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `COHERE_API_KEY` | string | ✅ Yes | - | Cohere API authentication |
| `QDRANT_URL` | string | ✅ Yes | - | Qdrant cluster URL |
| `QDRANT_API_KEY` | string | ✅ Yes | - | Qdrant API authentication |
| `QDRANT_COLLECTION_NAME` | string | ❌ No | `physical_ai_book` | Collection identifier |
| `WEBSITE_BASE_URL` | string | ❌ No | `http://localhost:3000` | Docusaurus site URL |
| `CHUNK_SIZE` | int | ❌ No | `800` | Words per chunk |
| `CHUNK_OVERLAP` | int | ❌ No | `100` | Overlap words |
| `EMBEDDING_MODEL` | string | ❌ No | `embed-english-v3.0` | Cohere model |
| `EMBEDDING_INPUT_TYPE` | string | ❌ No | `search_document` | Embedding type |

### 7.2 Configuration Loading

**Implementation**:
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load from .env file

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY is required")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
```

**Validation**:
- Required vars: Raise error if missing
- Optional vars: Use sensible defaults
- Type conversion: Cast to int/bool as needed
- Early validation: Fail fast if misconfigured

### 7.3 Configuration Management

**.env File** (not committed):
```env
COHERE_API_KEY=abc123...
QDRANT_URL=https://xyz.qdrant.io
QDRANT_API_KEY=xyz789...
WEBSITE_BASE_URL=https://mysite.com
```

**.env.example** (committed to git):
```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
```

**Security**:
- Never commit `.env` to git
- Use `.gitignore` to exclude `.env`
- Provide `.env.example` as template
- Document required variables

---

## 8. Validation Steps

### 8.1 Pre-Ingestion Validation

**Check 1: Dependencies**
```bash
python check_setup.py
```

Verifies:
- ✅ All Python packages installed
- ✅ Config file exists and valid
- ✅ API keys are set
- ✅ Cohere API connection works
- ✅ Qdrant connection works
- ✅ Website is accessible

**Expected Output**:
```
✓ All checks passed!
Ready to run pipeline.
```

### 8.2 Ingestion Validation

**During Pipeline**:

Track and log:
```
[Step 1/5] Crawling website...
  ✓ Extracted 50 documents

[Step 2/5] Chunking documents...
  ✓ Created 387 chunks

[Step 3/5] Generating embeddings...
  ✓ Generated embeddings for 387 chunks

[Step 4/5] Setting up vector store...
  ✓ Collection created

[Step 5/5] Inserting into vector store...
  ✓ Inserted 387 points
```

**Intermediate Validation**:
- After crawling: Check documents > 0
- After chunking: Check chunks > 0
- After embedding: Check embeddings.length == chunks.length
- After upload: Check collection.points_count > 0

### 8.3 Post-Ingestion Validation

**Check 1: Collection Stats**
```python
info = qdrant.get_collection("physical_ai_book")
print(f"Points: {info.points_count}")
print(f"Status: {info.status}")
```

**Expected**:
- Points count matches uploaded chunks
- Status: green/ready

**Check 2: Sample Search**
```bash
python search.py --sample-queries
```

**Expected Output**:
```
Query: "What is physical AI?"
[Result 1] Score: 0.8234
  Title: Understanding Physical AI
  URL: https://site.com/docs/module-01/chapter-01
  Text: Physical AI combines artificial intelligence...

[Result 2] Score: 0.7891
  ...
```

**Validation Criteria**:
- ✅ Search returns results (not empty)
- ✅ Scores are reasonable (0.5-1.0 range)
- ✅ Results are semantically relevant
- ✅ Metadata is populated correctly
- ✅ Text preview is clean (no HTML)

**Check 3: Metadata Integrity**
```python
# Verify all chunks have required fields
results = qdrant.scroll(collection_name, limit=100)
for point in results:
    assert 'text' in point.payload
    assert 'url' in point.payload
    assert 'chunk_id' in point.payload
```

### 8.4 Quality Validation

**Manual Spot Checks**:

1. **Content Quality**: Inspect `output/1_documents.json`
   - ✅ No HTML tags in content
   - ✅ No navigation text
   - ✅ Headings preserved
   - ✅ Text is coherent

2. **Chunk Quality**: Inspect `output/2_chunks.json`
   - ✅ Reasonable chunk sizes
   - ✅ Headings included in chunks
   - ✅ Metadata fields populated
   - ✅ No excessively short/long chunks

3. **Search Quality**: Test diverse queries
   - ✅ "What is X?" returns definitions
   - ✅ "How to X?" returns instructions
   - ✅ Module filter works correctly
   - ✅ Scores reflect relevance

**Automated Quality Checks**:
```python
# Check chunk size distribution
chunk_lengths = [len(c['text'].split()) for c in chunks]
avg_length = sum(chunk_lengths) / len(chunk_lengths)
assert 600 <= avg_length <= 1000  # Should be near target

# Check metadata completeness
for chunk in chunks:
    assert chunk.get('url') is not None
    assert chunk.get('title') is not None
    assert chunk.get('chunk_id') is not None
```

---

## 9. Implementation Timeline

**Phase 1: Setup** (30 min)
- Install dependencies
- Configure environment variables
- Verify API connections

**Phase 2: Core Pipeline** (2 hours)
- Implement crawler
- Implement chunker
- Implement embedder
- Implement vector store wrapper

**Phase 3: Orchestration** (1 hour)
- Implement main ingestion script
- Add error handling
- Add progress logging
- Add intermediate data saving

**Phase 4: Testing** (1 hour)
- Implement search utility
- Run on sample URLs
- Validate outputs
- Fix issues

**Phase 5: Documentation** (30 min)
- Write README
- Write quick start guide
- Document configuration

**Total Estimated Time**: 4-5 hours for complete implementation

---

## 10. Success Metrics

**Ingestion Success**:
- ✅ All seed URLs crawled successfully
- ✅ 95%+ pages extracted without errors
- ✅ All chunks have embeddings
- ✅ All points uploaded to Qdrant
- ✅ No data loss in pipeline

**Quality Metrics**:
- ✅ Average chunk size: 600-1000 words
- ✅ Chunk overlap: ~100 words
- ✅ Search results are relevant (manual validation)
- ✅ No HTML artifacts in text
- ✅ Metadata fields 100% populated

**Performance Metrics**:
- ⏱️ Crawling: < 5 sec per page
- ⏱️ Embedding: < 2 sec per batch
- ⏱️ Total time: < 15 min for 50 pages

**Reproducibility**:
- ✅ Can run pipeline multiple times (idempotent)
- ✅ Configuration via env vars only
- ✅ No hardcoded values
- ✅ Documented setup process

---

## 11. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Website unavailable | Pipeline fails | Early validation, clear error messages |
| API rate limits | Slow ingestion | Rate limiting, batch processing |
| Qdrant quota exceeded | Upload fails | Track usage, validate before upload |
| HTML structure changes | Bad extraction | Fallback selectors, manual inspection |
| Partial failures | Incomplete data | Continue on errors, log failures |
| API key exposure | Security breach | Use env vars, gitignore .env |

---

## 12. Future Enhancements (Out of Scope)

- Incremental updates (only changed pages)
- Multimodal embeddings (images, code)
- Hybrid search (keyword + vector)
- Metadata filtering (date ranges, authors)
- A/B testing different chunk sizes
- Evaluation metrics (NDCG, MRR)
- Monitoring and alerting
- Automated reingestion schedule

---

## Conclusion

This plan provides a complete blueprint for implementing a robust, production-ready RAG ingestion pipeline. The architecture prioritizes:

1. **Correctness**: Proper extraction, chunking, and storage
2. **Reproducibility**: Configuration-driven, idempotent design
3. **Clarity**: Well-documented, modular code structure
4. **Reliability**: Comprehensive error handling and validation

The implementation follows best practices for RAG systems and is designed to be maintainable and extensible for future enhancements.
