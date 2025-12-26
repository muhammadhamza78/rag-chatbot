# Implementation Tasks: Retrieval Pipeline (Spec 2)

**Objective**: Implement `retrieve.py` - a single Python script for retrieval and validation

**Target**: Backend engineers implementing the retrieval testing layer

**Status**: Ready for implementation

---

## Task Overview

| Task # | Task Name | Duration | Dependencies |
|--------|-----------|----------|--------------|
| 1 | Project Setup | 15 min | Spec 1 complete |
| 2 | Configuration Loading | 30 min | Task 1 |
| 3 | Qdrant Connection | 30 min | Task 2 |
| 4 | Query Embedding Generation | 30 min | Task 3 |
| 5 | Retrieval Function | 45 min | Task 4 |
| 6 | Metadata Validation | 45 min | Task 5 |
| 7 | Content Quality Validation | 45 min | Task 5 |
| 8 | Test Query Suite | 30 min | Task 5 |
| 9 | Validation Execution | 45 min | Tasks 6-8 |
| 10 | Result Display | 30 min | Task 9 |
| 11 | CLI Interface | 45 min | Task 10 |
| 12 | Error Handling | 30 min | All functions |
| 13 | Testing & Debugging | 1 hour | Tasks 1-12 |
| 14 | Documentation | 30 min | Task 13 |
| **Total** | | **~6.5 hours** | |

---

## Task 1: Project Setup

**Duration**: 15 minutes

**Objective**: Ensure environment is ready for implementation

### Deliverables

- [x] Virtual environment activated
- [x] Required packages installed
- [x] `.env` file configured
- [x] Qdrant collection verified

### Steps

1. **Activate Virtual Environment**
   ```bash
   cd rag-pipeline
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

2. **Verify Existing Dependencies**
   ```bash
   pip list | grep -E "cohere|qdrant|dotenv"
   ```

   Expected packages (from Spec 1):
   - `cohere==5.12.1`
   - `qdrant-client==1.12.0`
   - `python-dotenv==1.0.1`

3. **Install Additional Dependencies** (if needed)
   ```bash
   # No new dependencies required - all from Spec 1
   ```

4. **Verify Configuration**
   ```bash
   # Check .env file exists
   ls -la .env

   # Verify required variables
   cat .env | grep -E "COHERE|QDRANT"
   ```

5. **Verify Qdrant Collection**
   ```bash
   # Run existing check
   python check_setup.py
   ```

### Acceptance Criteria

- ✅ Virtual environment active
- ✅ All required packages installed
- ✅ `.env` file contains valid API keys
- ✅ Qdrant collection exists with embeddings
- ✅ `check_setup.py` passes all checks

### Files Modified

- None (setup only)

---

## Task 2: Configuration Loading

**Duration**: 30 minutes

**Objective**: Load and validate configuration from `.env`

### Deliverables

- [ ] `load_configuration()` function
- [ ] Configuration validation
- [ ] Clear error messages

### Implementation

Create `retrieve.py` and add:

```python
#!/usr/bin/env python3
"""
RAG Pipeline Retrieval and Validation Script

Purpose:
    Query Qdrant vector database and validate retrieval quality

Usage:
    python retrieve.py                          # Run validation suite
    python retrieve.py --query "your query"     # Single query
    python retrieve.py --interactive            # Interactive mode
"""

import os
from dotenv import load_dotenv


def load_configuration():
    """
    Load configuration from environment variables.

    Returns:
        dict: Configuration dictionary with all required settings

    Raises:
        ValueError: If required configuration is missing

    Example:
        >>> config = load_configuration()
        >>> print(config['collection_name'])
        physical_ai_book
    """
    # Load .env file
    load_dotenv()

    config = {
        # Required settings
        'cohere_api_key': os.getenv('COHERE_API_KEY'),
        'qdrant_url': os.getenv('QDRANT_URL'),
        'qdrant_api_key': os.getenv('QDRANT_API_KEY'),

        # Collection settings
        'collection_name': os.getenv('QDRANT_COLLECTION_NAME', 'physical_ai_book'),

        # Embedding settings
        'embedding_model': os.getenv('EMBEDDING_MODEL', 'embed-english-v3.0'),

        # Retrieval settings
        'default_top_k': int(os.getenv('DEFAULT_TOP_K', '5')),
        'min_relevance_score': float(os.getenv('MIN_RELEVANCE_SCORE', '0.6')),
    }

    # Validate required settings
    required = ['cohere_api_key', 'qdrant_url', 'qdrant_api_key']
    missing = [k for k in required if not config[k]]

    if missing:
        raise ValueError(
            f"Missing required configuration: {', '.join(missing)}\n"
            f"Please ensure .env file contains these variables."
        )

    return config


# Test function
if __name__ == '__main__':
    print("Testing configuration loading...")
    try:
        config = load_configuration()
        print("✓ Configuration loaded successfully")
        print(f"  Collection: {config['collection_name']}")
        print(f"  Model: {config['embedding_model']}")
        print(f"  Top-K: {config['default_top_k']}")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
```

### Testing

```bash
python retrieve.py
```

**Expected Output**:
```
Testing configuration loading...
✓ Configuration loaded successfully
  Collection: physical_ai_book
  Model: embed-english-v3.0
  Top-K: 5
```

### Acceptance Criteria

- ✅ Loads all configuration from `.env`
- ✅ Validates required settings
- ✅ Provides defaults for optional settings
- ✅ Raises clear error if config missing
- ✅ Test code runs successfully

### Files Created

- `retrieve.py` (started)

---

## Task 3: Qdrant Connection

**Duration**: 30 minutes

**Objective**: Connect to Qdrant and verify collection exists

### Deliverables

- [ ] `connect_to_qdrant()` function
- [ ] Collection verification
- [ ] Connection error handling

### Implementation

Add to `retrieve.py`:

```python
from qdrant_client import QdrantClient


def connect_to_qdrant(config):
    """
    Establish connection to Qdrant and verify collection exists.

    Args:
        config (dict): Configuration dictionary

    Returns:
        QdrantClient: Connected Qdrant client

    Raises:
        ConnectionError: If connection fails
        ValueError: If collection doesn't exist

    Example:
        >>> config = load_configuration()
        >>> client = connect_to_qdrant(config)
        >>> print("Connected!")
    """
    try:
        # Connect to Qdrant
        client = QdrantClient(
            url=config['qdrant_url'],
            api_key=config['qdrant_api_key']
        )

        # Verify collection exists
        collection_name = config['collection_name']
        collections = client.get_collections().collections
        collection_exists = any(c.name == collection_name for c in collections)

        if not collection_exists:
            available = [c.name for c in collections]
            raise ValueError(
                f"Collection '{collection_name}' not found.\n"
                f"Available collections: {available}"
            )

        # Get collection info
        collection_info = client.get_collection(collection_name)

        print(f"✓ Connected to Qdrant")
        print(f"  Collection: {collection_name}")
        print(f"  Points: {collection_info.points_count}")
        print(f"  Vectors: {collection_info.vectors_count}")
        print()

        return client

    except Exception as e:
        raise ConnectionError(f"Failed to connect to Qdrant: {e}")


# Update test code
if __name__ == '__main__':
    print("Testing Qdrant connection...")
    try:
        config = load_configuration()
        client = connect_to_qdrant(config)
        print("✓ Connection test passed")
    except (ValueError, ConnectionError) as e:
        print(f"✗ Connection error: {e}")
```

### Testing

```bash
python retrieve.py
```

**Expected Output**:
```
Testing Qdrant connection...
✓ Connected to Qdrant
  Collection: physical_ai_book
  Points: 387
  Vectors: 387

✓ Connection test passed
```

### Acceptance Criteria

- ✅ Connects to Qdrant successfully
- ✅ Verifies collection exists
- ✅ Retrieves collection statistics
- ✅ Handles connection errors gracefully
- ✅ Handles missing collection error
- ✅ Test code runs successfully

### Files Modified

- `retrieve.py`

---

## Task 4: Query Embedding Generation

**Duration**: 30 minutes

**Objective**: Generate embeddings for user queries using Cohere

### Deliverables

- [ ] `generate_query_embedding()` function
- [ ] Cohere API integration
- [ ] Timing measurements

### Implementation

Add to `retrieve.py`:

```python
import cohere
import time


def generate_query_embedding(query, config):
    """
    Generate embedding for search query using Cohere.

    Args:
        query (str): User query text
        config (dict): Configuration dictionary

    Returns:
        list: Query embedding vector (1024 dimensions)

    Raises:
        Exception: If embedding generation fails

    Example:
        >>> config = load_configuration()
        >>> embedding = generate_query_embedding("What is AI?", config)
        >>> print(f"Dimension: {len(embedding)}")
        Dimension: 1024
    """
    try:
        start_time = time.time()

        # Initialize Cohere client
        client = cohere.Client(config['cohere_api_key'])

        # Generate embedding
        response = client.embed(
            texts=[query],
            model=config['embedding_model'],
            input_type='search_query'  # Important: search_query not search_document
        )

        embedding = response.embeddings[0]
        elapsed = time.time() - start_time

        print(f"✓ Generated query embedding ({elapsed:.2f}s)")
        print(f"  Dimension: {len(embedding)}")
        print()

        return embedding

    except Exception as e:
        raise Exception(f"Failed to generate query embedding: {e}")


# Update test code
if __name__ == '__main__':
    print("Testing query embedding generation...")
    try:
        config = load_configuration()
        embedding = generate_query_embedding("What is physical AI?", config)
        print(f"✓ Embedding test passed (dimension: {len(embedding)})")
    except Exception as e:
        print(f"✗ Embedding error: {e}")
```

### Testing

```bash
python retrieve.py
```

**Expected Output**:
```
Testing query embedding generation...
✓ Generated query embedding (0.23s)
  Dimension: 1024

✓ Embedding test passed (dimension: 1024)
```

### Acceptance Criteria

- ✅ Generates 1024-dimensional embeddings
- ✅ Uses `input_type='search_query'`
- ✅ Tracks generation time
- ✅ Handles API errors gracefully
- ✅ Test code runs successfully

### Files Modified

- `retrieve.py`

---

## Task 5: Retrieval Function

**Duration**: 45 minutes

**Objective**: Implement similarity search and result retrieval

### Deliverables

- [ ] `retrieve_chunks()` function
- [ ] Similarity search implementation
- [ ] Result formatting with metadata
- [ ] Module filtering support

### Implementation

Add to `retrieve.py`:

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue


def retrieve_chunks(client, query_embedding, config, top_k=None, module_filter=None):
    """
    Retrieve relevant chunks from Qdrant using similarity search.

    Args:
        client (QdrantClient): Connected Qdrant client
        query_embedding (list): Query embedding vector
        config (dict): Configuration dictionary
        top_k (int, optional): Number of results to return
        module_filter (str, optional): Filter by module name

    Returns:
        list: Retrieved chunks with metadata and scores

    Example:
        >>> chunks = retrieve_chunks(client, embedding, config, top_k=5)
        >>> print(f"Retrieved {len(chunks)} chunks")
        >>> print(f"Top score: {chunks[0]['score']:.3f}")
    """
    if top_k is None:
        top_k = config['default_top_k']

    try:
        start_time = time.time()

        # Build filter if module specified
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

        # Perform similarity search
        results = client.search(
            collection_name=config['collection_name'],
            query_vector=query_embedding,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
            with_vectors=False  # Don't return vectors (save bandwidth)
        )

        elapsed = time.time() - start_time

        print(f"✓ Retrieved {len(results)} chunks ({elapsed:.2f}s)")
        print()

        # Format results
        chunks = []
        for result in results:
            chunk = {
                'score': result.score,
                'text': result.payload.get('text', ''),
                'url': result.payload.get('url', ''),
                'title': result.payload.get('title', ''),
                'module': result.payload.get('module'),
                'heading_hierarchy': result.payload.get('heading_hierarchy', ''),
                'chunk_index': result.payload.get('chunk_index'),
                'total_chunks': result.payload.get('total_chunks'),
                'chunk_id': result.payload.get('chunk_id', ''),
            }
            chunks.append(chunk)

        return chunks

    except Exception as e:
        raise Exception(f"Failed to retrieve chunks: {e}")


# Update test code
if __name__ == '__main__':
    print("Testing retrieval...")
    try:
        config = load_configuration()
        client = connect_to_qdrant(config)
        embedding = generate_query_embedding("What is physical AI?", config)
        chunks = retrieve_chunks(client, embedding, config)

        print(f"✓ Retrieval test passed")
        print(f"  Retrieved: {len(chunks)} chunks")
        print(f"  Top score: {chunks[0]['score']:.4f}")
        print(f"  Top title: {chunks[0]['title']}")
    except Exception as e:
        print(f"✗ Retrieval error: {e}")
```

### Testing

```bash
python retrieve.py
```

**Expected Output**:
```
Testing retrieval...
✓ Connected to Qdrant
  Collection: physical_ai_book
  Points: 387

✓ Generated query embedding (0.23s)
  Dimension: 1024

✓ Retrieved 5 chunks (0.31s)

✓ Retrieval test passed
  Retrieved: 5 chunks
  Top score: 0.8456
  Top title: Understanding Physical AI
```

### Acceptance Criteria

- ✅ Performs similarity search
- ✅ Returns top-K results
- ✅ Includes all metadata fields
- ✅ Supports module filtering
- ✅ Tracks search time
- ✅ Test code runs successfully

### Files Modified

- `retrieve.py`

---

## Task 6: Metadata Validation

**Duration**: 45 minutes

**Objective**: Validate metadata completeness and correctness

### Deliverables

- [ ] `validate_metadata()` function
- [ ] Required field checks
- [ ] Format validation
- [ ] Range validation

### Implementation

Add to `retrieve.py`:

```python
def validate_metadata(chunks):
    """
    Validate metadata completeness and correctness.

    Args:
        chunks (list): Retrieved chunks with metadata

    Returns:
        dict: Validation results with pass/fail status

    Example:
        >>> results = validate_metadata(chunks)
        >>> print(f"Passed: {results['passed']}/{results['total_chunks']}")
    """
    validation_results = {
        'total_chunks': len(chunks),
        'passed': 0,
        'failed': 0,
        'issues': []
    }

    required_fields = ['text', 'url', 'title', 'chunk_id']

    for i, chunk in enumerate(chunks):
        chunk_issues = []

        # Check required fields
        for field in required_fields:
            if not chunk.get(field):
                chunk_issues.append(f"Missing or empty '{field}'")

        # Validate URL format
        url = chunk.get('url', '')
        if url and not (url.startswith('http://') or url.startswith('https://')):
            chunk_issues.append(f"Invalid URL format: {url}")

        # Validate chunk index
        chunk_index = chunk.get('chunk_index')
        total_chunks = chunk.get('total_chunks')
        if chunk_index is not None and total_chunks is not None:
            if not (0 <= chunk_index < total_chunks):
                chunk_issues.append(
                    f"Invalid chunk index: {chunk_index}/{total_chunks}"
                )

        # Validate score range
        score = chunk.get('score', 0)
        if not (0.0 <= score <= 1.0):
            chunk_issues.append(f"Score out of range: {score}")

        # Record results
        if chunk_issues:
            validation_results['failed'] += 1
            validation_results['issues'].append({
                'chunk_index': i,
                'chunk_id': chunk.get('chunk_id', 'unknown'),
                'issues': chunk_issues
            })
        else:
            validation_results['passed'] += 1

    return validation_results


# Update test code to include validation
if __name__ == '__main__':
    print("Testing metadata validation...")
    try:
        config = load_configuration()
        client = connect_to_qdrant(config)
        embedding = generate_query_embedding("What is physical AI?", config)
        chunks = retrieve_chunks(client, embedding, config)

        # Validate metadata
        metadata_results = validate_metadata(chunks)

        print(f"✓ Metadata validation test passed")
        print(f"  Passed: {metadata_results['passed']}/{metadata_results['total_chunks']}")
        print(f"  Failed: {metadata_results['failed']}")

        if metadata_results['issues']:
            print("  Issues:")
            for issue in metadata_results['issues'][:3]:
                print(f"    - Chunk {issue['chunk_index']}: {', '.join(issue['issues'])}")

    except Exception as e:
        print(f"✗ Validation error: {e}")
```

### Testing

```bash
python retrieve.py
```

**Expected Output**:
```
✓ Metadata validation test passed
  Passed: 5/5
  Failed: 0
```

### Acceptance Criteria

- ✅ Checks all required fields
- ✅ Validates URL format
- ✅ Validates chunk indices
- ✅ Validates score range
- ✅ Returns detailed issue list
- ✅ Test code runs successfully

### Files Modified

- `retrieve.py`

---

## Task 7: Content Quality Validation

**Duration**: 45 minutes

**Objective**: Check for HTML artifacts and text quality

### Deliverables

- [ ] `validate_content_quality()` function
- [ ] HTML artifact detection
- [ ] UI text detection
- [ ] Whitespace validation

### Implementation

Add to `retrieve.py`:

```python
def validate_content_quality(chunks):
    """
    Validate content quality (no HTML, clean text).

    Args:
        chunks (list): Retrieved chunks with text content

    Returns:
        dict: Quality validation results

    Example:
        >>> results = validate_content_quality(chunks)
        >>> print(f"Clean: {results['clean']}/{results['total_chunks']}")
    """
    quality_results = {
        'total_chunks': len(chunks),
        'clean': 0,
        'has_issues': 0,
        'issues': []
    }

    # HTML artifact patterns
    html_patterns = [
        '<', '>',           # HTML tags
        '&lt;', '&gt;',     # Encoded tags
        'class=', 'id=',    # HTML attributes
        'href=', 'src=',    # Link/image attributes
    ]

    # UI text patterns
    ui_patterns = [
        'Next »', '« Previous',
        'Edit this page',
        'Table of Contents',
        'Skip to content',
    ]

    for i, chunk in enumerate(chunks):
        text = chunk.get('text', '')
        chunk_issues = []

        # Check for HTML artifacts
        for pattern in html_patterns:
            if pattern in text:
                chunk_issues.append(f"HTML artifact found: '{pattern}'")
                break

        # Check for UI text
        for pattern in ui_patterns:
            if pattern in text:
                chunk_issues.append(f"UI text found: '{pattern}'")
                break

        # Check for excessive whitespace
        if '   ' in text or '\n\n\n' in text:
            chunk_issues.append("Excessive whitespace detected")

        # Check text is not empty
        if not text.strip():
            chunk_issues.append("Empty or whitespace-only text")

        # Record results
        if chunk_issues:
            quality_results['has_issues'] += 1
            quality_results['issues'].append({
                'chunk_index': i,
                'chunk_id': chunk.get('chunk_id', 'unknown'),
                'issues': chunk_issues,
                'text_preview': text[:100] + '...' if len(text) > 100 else text
            })
        else:
            quality_results['clean'] += 1

    return quality_results


# Update test code
if __name__ == '__main__':
    print("Testing content quality validation...")
    try:
        config = load_configuration()
        client = connect_to_qdrant(config)
        embedding = generate_query_embedding("What is physical AI?", config)
        chunks = retrieve_chunks(client, embedding, config)

        # Validate content quality
        quality_results = validate_content_quality(chunks)

        print(f"✓ Content quality validation test passed")
        print(f"  Clean: {quality_results['clean']}/{quality_results['total_chunks']}")
        print(f"  Has issues: {quality_results['has_issues']}")

        if quality_results['issues']:
            print("  Issues:")
            for issue in quality_results['issues'][:3]:
                print(f"    - Chunk {issue['chunk_index']}: {', '.join(issue['issues'])}")

    except Exception as e:
        print(f"✗ Validation error: {e}")
```

### Testing

```bash
python retrieve.py
```

**Expected Output**:
```
✓ Content quality validation test passed
  Clean: 5/5
  Has issues: 0
```

### Acceptance Criteria

- ✅ Detects HTML artifacts
- ✅ Detects UI text
- ✅ Detects excessive whitespace
- ✅ Checks for empty text
- ✅ Returns detailed issue list
- ✅ Test code runs successfully

### Files Modified

- `retrieve.py`

---

## Task 8: Test Query Suite

**Duration**: 30 minutes

**Objective**: Define comprehensive test queries

### Deliverables

- [ ] `get_test_queries()` function
- [ ] 8+ test queries
- [ ] Expected behavior definitions

### Implementation

Add to `retrieve.py`:

```python
def get_test_queries():
    """
    Get predefined test queries covering various modules and query types.

    Returns:
        list: Test query definitions with expected behavior

    Example:
        >>> queries = get_test_queries()
        >>> print(f"Total test queries: {len(queries)}")
        Total test queries: 8
    """
    return [
        {
            'id': 'Q001',
            'query': 'What is physical AI?',
            'type': 'definitional',
            'expected_modules': ['module-01'],
            'expected_keywords': ['physical AI', 'intelligent', 'systems'],
            'min_score': 0.65,
            'description': 'Basic definitional query about core concept'
        },
        {
            'id': 'Q002',
            'query': 'How to simulate sensors in Gazebo?',
            'type': 'procedural',
            'expected_modules': ['module-02'],
            'expected_keywords': ['Gazebo', 'sensor', 'simulation'],
            'min_score': 0.60,
            'description': 'Procedural query about specific tool'
        },
        {
            'id': 'Q003',
            'query': 'Explain digital twins',
            'type': 'conceptual',
            'expected_modules': ['module-02'],
            'expected_keywords': ['digital twin', 'virtual', 'representation'],
            'min_score': 0.65,
            'description': 'Conceptual explanation request'
        },
        {
            'id': 'Q004',
            'query': 'What are sensors in robotics?',
            'type': 'definitional',
            'expected_modules': ['module-01', 'module-02'],
            'expected_keywords': ['sensor', 'robot', 'measure'],
            'min_score': 0.60,
            'description': 'Cross-module concept query'
        },
        {
            'id': 'Q005',
            'query': 'Unity rendering',
            'type': 'technical',
            'expected_modules': ['module-02'],
            'expected_keywords': ['Unity', 'render', 'visual'],
            'min_score': 0.55,
            'description': 'Short technical query (2 words)'
        },
        {
            'id': 'Q006',
            'query': 'How does physics simulation work in robotics?',
            'type': 'conceptual',
            'expected_modules': ['module-02'],
            'expected_keywords': ['physics', 'simulation', 'robotics'],
            'min_score': 0.60,
            'description': 'Longer conceptual query'
        },
        {
            'id': 'Q007',
            'query': 'ROS',
            'type': 'technical',
            'expected_modules': ['module-02', 'module-03'],
            'expected_keywords': ['ROS', 'Robot Operating System'],
            'min_score': 0.50,
            'description': 'Very short query (1 word, acronym)'
        },
        {
            'id': 'Q008',
            'query': 'Difference between simulation and real world',
            'type': 'comparative',
            'expected_modules': ['module-02'],
            'expected_keywords': ['simulation', 'real', 'difference'],
            'min_score': 0.55,
            'description': 'Comparative query'
        },
    ]


# Test function
if __name__ == '__main__':
    print("Testing query suite...")
    queries = get_test_queries()
    print(f"✓ Query suite loaded: {len(queries)} queries")
    print("\nQuery types:")
    types = {}
    for q in queries:
        types[q['type']] = types.get(q['type'], 0) + 1
    for qtype, count in types.items():
        print(f"  - {qtype}: {count}")
```

### Testing

```bash
python retrieve.py
```

**Expected Output**:
```
Testing query suite...
✓ Query suite loaded: 8 queries

Query types:
  - definitional: 2
  - procedural: 1
  - conceptual: 2
  - technical: 2
  - comparative: 1
```

### Acceptance Criteria

- ✅ 8+ queries defined
- ✅ Multiple query types covered
- ✅ Expected behaviors specified
- ✅ Min score thresholds set
- ✅ Keywords defined for validation
- ✅ Test code runs successfully

### Files Modified

- `retrieve.py`

---

## Task 9: Validation Execution

**Duration**: 45 minutes

**Objective**: Execute test suite and validate results

### Deliverables

- [ ] `run_validation_suite()` function
- [ ] Query-by-query execution
- [ ] Result validation
- [ ] Summary generation

### Implementation

Add to `retrieve.py`:

```python
def run_validation_suite(client, config):
    """
    Run comprehensive validation suite with test queries.

    Args:
        client (QdrantClient): Connected Qdrant client
        config (dict): Configuration dictionary

    Returns:
        dict: Validation results summary

    Example:
        >>> results = run_validation_suite(client, config)
        >>> print(f"Pass rate: {results['passed']/results['total_queries']*100:.1f}%")
    """
    test_queries = get_test_queries()

    results = {
        'total_queries': len(test_queries),
        'passed': 0,
        'failed': 0,
        'query_results': []
    }

    print("=" * 80)
    print("RUNNING VALIDATION SUITE")
    print("=" * 80)
    print()

    for test in test_queries:
        print(f"[{test['id']}] {test['query']}")
        print(f"Type: {test['type']}")
        print(f"Description: {test['description']}")
        print("-" * 80)

        try:
            # Generate embedding
            query_embedding = generate_query_embedding(test['query'], config)

            # Retrieve chunks
            chunks = retrieve_chunks(client, query_embedding, config, top_k=5)

            # Validate results
            query_result = {
                'query_id': test['id'],
                'query': test['query'],
                'chunks_retrieved': len(chunks),
                'passed': True,
                'issues': []
            }

            # Check: Results returned
            if len(chunks) == 0:
                query_result['passed'] = False
                query_result['issues'].append('No results returned')

            # Check: Top result score meets minimum
            if chunks and chunks[0]['score'] < test['min_score']:
                query_result['passed'] = False
                query_result['issues'].append(
                    f"Top score {chunks[0]['score']:.3f} < minimum {test['min_score']}"
                )

            # Check: Expected keywords present (at least one)
            if chunks and test.get('expected_keywords'):
                top_text = chunks[0]['text'].lower()
                has_keyword = any(
                    kw.lower() in top_text
                    for kw in test['expected_keywords']
                )
                if not has_keyword:
                    query_result['passed'] = False
                    query_result['issues'].append(
                        f"No expected keywords found in top result"
                    )

            # Display results
            if query_result['passed']:
                results['passed'] += 1
                print(f"✓ PASSED")
            else:
                results['failed'] += 1
                print(f"✗ FAILED")
                for issue in query_result['issues']:
                    print(f"  - {issue}")

            # Show top result
            if chunks:
                print(f"\nTop Result:")
                print(f"  Score: {chunks[0]['score']:.4f}")
                print(f"  Title: {chunks[0]['title']}")
                print(f"  Module: {chunks[0].get('module', 'N/A')}")
                print(f"  Preview: {chunks[0]['text'][:150]}...")

            results['query_results'].append(query_result)

        except Exception as e:
            print(f"✗ ERROR: {e}")
            results['failed'] += 1
            results['query_results'].append({
                'query_id': test['id'],
                'query': test['query'],
                'passed': False,
                'error': str(e)
            })

        print()
        print()

    return results
```

### Testing

Remove test code and add new main:

```python
if __name__ == '__main__':
    print("Running validation suite...")
    try:
        config = load_configuration()
        client = connect_to_qdrant(config)
        results = run_validation_suite(client, config)

        # Display summary
        print("=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total Queries: {results['total_queries']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Pass Rate: {results['passed']/results['total_queries']*100:.1f}%")

    except Exception as e:
        print(f"ERROR: {e}")
```

### Testing

```bash
python retrieve.py
```

**Expected Output**: Full validation suite execution

### Acceptance Criteria

- ✅ Runs all 8 test queries
- ✅ Validates each result
- ✅ Shows pass/fail for each query
- ✅ Displays top result details
- ✅ Generates summary statistics
- ✅ Handles errors gracefully

### Files Modified

- `retrieve.py`

---

## Task 10: Result Display

**Duration**: 30 minutes

**Objective**: Format and display results clearly

### Deliverables

- [ ] `display_retrieval_results()` function
- [ ] Formatted console output
- [ ] Metadata display

### Implementation

Add to `retrieve.py`:

```python
def display_retrieval_results(query, chunks, elapsed_time=None):
    """
    Display retrieval results in a formatted, readable way.

    Args:
        query (str): Original query
        chunks (list): Retrieved chunks
        elapsed_time (float, optional): Total retrieval time

    Example:
        >>> display_retrieval_results("What is AI?", chunks, 0.54)
    """
    print("=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    if elapsed_time:
        print(f"Total Time: {elapsed_time:.2f}s")

    print(f"Results: {len(chunks)}")
    print()

    for i, chunk in enumerate(chunks, 1):
        print(f"[{i}] Score: {chunk['score']:.4f}")
        print(f"    Title: {chunk['title']}")
        print(f"    URL: {chunk['url']}")

        if chunk.get('module'):
            print(f"    Module: {chunk['module']}")

        if chunk.get('heading_hierarchy'):
            print(f"    Section: {chunk['heading_hierarchy']}")

        if chunk.get('chunk_index') is not None:
            print(f"    Chunk: {chunk['chunk_index']}/{chunk.get('total_chunks', '?')}")

        # Show text preview
        text = chunk['text']
        preview_length = 200
        if len(text) > preview_length:
            preview = text[:preview_length] + "..."
        else:
            preview = text

        print(f"\n    Text:")
        for line in preview.split('\n'):
            if line.strip():
                print(f"    {line}")

        print()
        print("-" * 80)
        print()
```

### Acceptance Criteria

- ✅ Clear, readable output format
- ✅ Shows all metadata fields
- ✅ Displays text preview
- ✅ Indicates timing information
- ✅ Properly formatted for console

### Files Modified

- `retrieve.py`

---

## Task 11: CLI Interface

**Duration**: 45 minutes

**Objective**: Add command-line interface with multiple modes

### Deliverables

- [ ] Argument parsing
- [ ] Validation mode
- [ ] Single query mode
- [ ] Interactive mode

### Implementation

Add to `retrieve.py`:

```python
import argparse
import sys


def main():
    """
    Main execution function for retrieval and validation.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='RAG Pipeline Retrieval and Validation'
    )
    parser.add_argument(
        '--query',
        type=str,
        help='Single query to test'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Run full validation suite'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive query mode'
    )
    parser.add_argument(
        '--module',
        type=str,
        help='Filter results by module'
    )
    parser.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='Number of results to return (default: 5)'
    )

    args = parser.parse_args()

    try:
        # Load configuration
        print("Loading configuration...")
        config = load_configuration()
        print("✓ Configuration loaded")
        print()

        # Connect to Qdrant
        print("Connecting to Qdrant...")
        client = connect_to_qdrant(config)

        # Run requested mode
        if args.validate:
            # Run validation suite
            results = run_validation_suite(client, config)

            # Display summary
            print("=" * 80)
            print("VALIDATION SUMMARY")
            print("=" * 80)
            print(f"Total Queries: {results['total_queries']}")
            print(f"Passed: {results['passed']}")
            print(f"Failed: {results['failed']}")
            print(f"Pass Rate: {results['passed']/results['total_queries']*100:.1f}%")
            print()

            sys.exit(0 if results['failed'] == 0 else 1)

        elif args.interactive:
            # Interactive mode
            print("Interactive Mode (type 'exit' to quit)")
            print()

            while True:
                query = input("Query: ").strip()

                if query.lower() in ['exit', 'quit', 'q']:
                    break

                if not query:
                    continue

                # Process query
                embedding = generate_query_embedding(query, config)
                chunks = retrieve_chunks(
                    client,
                    embedding,
                    config,
                    top_k=args.top_k,
                    module_filter=args.module
                )

                display_retrieval_results(query, chunks)

        elif args.query:
            # Single query mode
            start_time = time.time()

            embedding = generate_query_embedding(args.query, config)
            chunks = retrieve_chunks(
                client,
                embedding,
                config,
                top_k=args.top_k,
                module_filter=args.module
            )

            elapsed = time.time() - start_time

            display_retrieval_results(args.query, chunks, elapsed)

            # Run validation
            print("Metadata Validation:")
            metadata_validation = validate_metadata(chunks)
            print(f"  Passed: {metadata_validation['passed']}/{metadata_validation['total_chunks']}")
            print()

            print("Content Quality Validation:")
            quality_validation = validate_content_quality(chunks)
            print(f"  Clean: {quality_validation['clean']}/{quality_validation['total_chunks']}")
            print()

        else:
            # Default: run validation
            results = run_validation_suite(client, config)

            # Display summary
            print("=" * 80)
            print("VALIDATION SUMMARY")
            print("=" * 80)
            print(f"Total Queries: {results['total_queries']}")
            print(f"Passed: {results['passed']}")
            print(f"Failed: {results['failed']}")
            print(f"Pass Rate: {results['passed']/results['total_queries']*100:.1f}%")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### Testing

```bash
# Test validation mode
python retrieve.py --validate

# Test single query
python retrieve.py --query "What is physical AI?"

# Test interactive mode
python retrieve.py --interactive

# Test module filter
python retrieve.py --query "sensors" --module module-01
```

### Acceptance Criteria

- ✅ All CLI modes work
- ✅ Arguments parse correctly
- ✅ Module filtering works
- ✅ Top-K parameter works
- ✅ Default mode is validation
- ✅ Interactive mode accepts multiple queries

### Files Modified

- `retrieve.py`

---

## Task 12: Error Handling

**Duration**: 30 minutes

**Objective**: Add comprehensive error handling

### Deliverables

- [ ] Configuration error handling
- [ ] Connection error handling
- [ ] Empty result handling
- [ ] API error handling

### Implementation

Review and enhance error handling in all functions:

1. **Configuration errors** - Already handled in `load_configuration()`
2. **Connection errors** - Already handled in `connect_to_qdrant()`
3. **API errors** - Already handled in `generate_query_embedding()`
4. **Empty results** - Add warning in retrieval

Enhance `retrieve_chunks()`:

```python
# After retrieving chunks
if not chunks:
    print("⚠ No results found for this query")
    print("This could indicate:")
    print("  - Query is too specific")
    print("  - Collection is empty")
    print("  - Module filter too restrictive")
```

### Testing

Test error conditions:

```bash
# Test with invalid module filter
python retrieve.py --query "test" --module "invalid-module"

# Test with very specific query (might return no results)
python retrieve.py --query "xyzabc123nonexistent"
```

### Acceptance Criteria

- ✅ Clear error messages for all failure modes
- ✅ Graceful handling of missing config
- ✅ Helpful suggestions for common errors
- ✅ No uncaught exceptions
- ✅ Proper exit codes

### Files Modified

- `retrieve.py`

---

## Task 13: Testing & Debugging

**Duration**: 1 hour

**Objective**: Comprehensive testing of all functionality

### Test Checklist

#### Configuration Tests
- [ ] Test with valid `.env` file
- [ ] Test with missing `.env` file
- [ ] Test with missing required variables
- [ ] Test with invalid variable types

#### Connection Tests
- [ ] Test Qdrant connection
- [ ] Test with invalid Qdrant URL
- [ ] Test with invalid API key
- [ ] Test with missing collection

#### Retrieval Tests
- [ ] Test successful query retrieval
- [ ] Test with module filter
- [ ] Test with different top-K values
- [ ] Test with empty results

#### Validation Tests
- [ ] Test metadata validation
- [ ] Test content quality validation
- [ ] Test validation suite (all 8 queries)
- [ ] Verify pass/fail logic

#### CLI Tests
- [ ] Test `--validate` mode
- [ ] Test `--query` mode
- [ ] Test `--interactive` mode
- [ ] Test module filter argument
- [ ] Test top-K argument

#### Edge Cases
- [ ] Very short query (1 word)
- [ ] Very long query (sentence)
- [ ] Query with special characters
- [ ] Non-existent module filter

### Testing Commands

```bash
# Full validation suite
python retrieve.py --validate

# Single queries
python retrieve.py --query "What is physical AI?"
python retrieve.py --query "sensors"
python retrieve.py --query "ROS"

# With filters
python retrieve.py --query "sensors" --module module-01
python retrieve.py --query "physics" --top-k 10

# Interactive mode
python retrieve.py --interactive
```

### Debugging

If issues arise:

1. **Enable verbose output**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check intermediate values**:
   ```python
   print(f"DEBUG: embedding length = {len(embedding)}")
   print(f"DEBUG: chunks retrieved = {len(chunks)}")
   ```

3. **Verify collection state**:
   ```bash
   python check_setup.py
   ```

### Acceptance Criteria

- ✅ All test cases pass
- ✅ No errors in normal usage
- ✅ Graceful error handling
- ✅ Performance targets met (<2s per query)
- ✅ Validation suite pass rate ≥75%

### Files Modified

- `retrieve.py` (bug fixes)

---

## Task 14: Documentation

**Duration**: 30 minutes

**Objective**: Complete inline and external documentation

### Deliverables

- [ ] Docstrings for all functions
- [ ] README section
- [ ] Usage examples
- [ ] Troubleshooting guide

### Implementation

1. **Verify Docstrings**

Ensure all functions have complete docstrings:
- Purpose description
- Args with types
- Returns with type
- Raises (errors)
- Example usage

2. **Add README Section**

Add to `README.md`:

````markdown
## Retrieval and Validation

### Overview

The `retrieve.py` script provides retrieval testing and validation for the RAG pipeline.

### Quick Test

Test retrieval with a single query:

```bash
python retrieve.py --query "What is physical AI?"
```

### Validation Suite

Run comprehensive validation with 8 test queries:

```bash
python retrieve.py --validate
```

This tests:
- Definitional queries ("What is X?")
- Procedural queries ("How to X?")
- Conceptual queries ("Explain X")
- Technical queries (short terms, acronyms)
- Cross-module queries
- Comparative queries

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
- 8 queries execute
- Each query shows pass/fail
- Top result displayed
- Final summary with pass rate

**Target**: ≥75% pass rate

**Single Query**:
- Results displayed with scores
- Metadata shown (URL, module, title)
- Text preview included
- Validation results (metadata & content quality)

### Troubleshooting

**No results found**:
- Query may be too specific
- Try broader terms
- Check module filter isn't too restrictive

**Low scores**:
- Expected for very short queries (1-2 words)
- Try longer, more specific queries

**Connection errors**:
- Verify `.env` file configured
- Check Qdrant cluster is running
- Run `python check_setup.py` first
````

3. **Create Usage Examples File**

Create `RETRIEVAL_USAGE.md`:

```markdown
# Retrieval Script Usage Examples

## Validation Suite

Default behavior - runs all 8 test queries:

```bash
python retrieve.py
# or explicitly
python retrieve.py --validate
```

## Single Queries

### Basic Query
```bash
python retrieve.py --query "What is physical AI?"
```

### With Module Filter
```bash
python retrieve.py --query "sensors" --module module-01
```

### More Results
```bash
python retrieve.py --query "simulation" --top-k 10
```

## Interactive Mode

```bash
python retrieve.py --interactive
```

Then:
```
Query: What is physical AI?
[Results displayed]

Query: digital twins
[Results displayed]

Query: exit
```

## Expected Results

- Retrieval: <2 seconds per query
- Top score: Usually >0.6 for good queries
- Metadata: 100% complete
- Content: 95%+ clean (no HTML)
```

### Acceptance Criteria

- ✅ All functions have docstrings
- ✅ README section added
- ✅ Usage examples provided
- ✅ Troubleshooting guide included
- ✅ File header comment complete

### Files Modified

- `retrieve.py` (docstrings)
- `README.md` (new section)
- `RETRIEVAL_USAGE.md` (new file)

---

## Summary Checklist

### Code Implementation

- [ ] Task 1: Project setup complete
- [ ] Task 2: Configuration loading implemented
- [ ] Task 3: Qdrant connection implemented
- [ ] Task 4: Query embedding generation implemented
- [ ] Task 5: Retrieval function implemented
- [ ] Task 6: Metadata validation implemented
- [ ] Task 7: Content quality validation implemented
- [ ] Task 8: Test query suite defined
- [ ] Task 9: Validation execution implemented
- [ ] Task 10: Result display implemented
- [ ] Task 11: CLI interface implemented
- [ ] Task 12: Error handling complete
- [ ] Task 13: Testing complete
- [ ] Task 14: Documentation complete

### Quality Checks

- [ ] All functions have docstrings
- [ ] Error handling comprehensive
- [ ] Performance targets met
- [ ] Validation suite passes ≥75%
- [ ] Code is readable and maintainable
- [ ] No hardcoded values
- [ ] Configuration from `.env`

### Documentation

- [ ] README section added
- [ ] Usage examples provided
- [ ] Troubleshooting guide included
- [ ] Function docstrings complete

### Testing

- [ ] Validation mode works
- [ ] Query mode works
- [ ] Interactive mode works
- [ ] Module filtering works
- [ ] Error cases handled gracefully

---

## Deliverables

### Code

- `retrieve.py` (~500-700 lines)

### Documentation

- README section (in `README.md`)
- Usage examples (`RETRIEVAL_USAGE.md`)
- Inline docstrings

### Validation

- Validation suite execution logs
- Performance metrics
- Quality metrics

---

## Timeline Summary

| Phase | Duration |
|-------|----------|
| Setup & Configuration | 45 min |
| Core Retrieval | 1.5 hours |
| Validation Logic | 1.5 hours |
| Test Suite & Execution | 1.25 hours |
| Display & CLI | 1.25 hours |
| Testing & Documentation | 1.5 hours |
| **Total** | **~6.5 hours** |

---

## Success Criteria

**Must Pass**:
1. ✅ `retrieve.py` runs without errors
2. ✅ Validation suite pass rate ≥75%
3. ✅ Metadata validation 100% pass
4. ✅ Content quality ≥95% clean
5. ✅ Performance <2s per query
6. ✅ All CLI modes functional
7. ✅ Documentation complete

**Ready for Production**:
- All tests pass
- Documentation complete
- Performance acceptable
- Error handling robust

---

## Next Steps After Implementation

1. Run full validation suite
2. Review failed queries (if any)
3. Document any pipeline issues found
4. Share validation report with team
5. Proceed to integration (if needed)

---

**Status**: Ready for implementation

**Estimated Time**: 6.5 hours

**Dependencies**: Spec 1 (ingestion) complete, Qdrant collection populated

**Next**: Begin Task 1 - Project Setup
