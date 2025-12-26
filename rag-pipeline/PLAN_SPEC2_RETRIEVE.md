# Plan: Retrieval and Pipeline Validation (Spec 2)

**Objective**: Design and implement `retrieve.py` - a single, cohesive Python script for querying Qdrant, retrieving relevant chunks, and validating the RAG pipeline.

**Version**: 1.0
**Date**: December 25, 2025

---

## 1. Overview

### Purpose

Create a standalone validation script that:
- Queries the Qdrant vector database
- Retrieves semantically relevant chunks
- Validates retrieval quality and metadata accuracy
- Provides clear console output for human review

### Design Philosophy

**Single Script Design**:
- Everything in one file (`retrieve.py`)
- Self-contained validation logic
- Minimal dependencies on other modules
- Clear, linear execution flow

**Validation First**:
- Built-in test queries
- Automatic relevance checking
- Metadata integrity validation
- Clear pass/fail reporting

---

## 2. Architecture Design

### 2.1 Script Structure

```python
# retrieve.py - Single-file retrieval and validation script

"""
RAG Pipeline Retrieval and Validation Script

Purpose:
    Query Qdrant vector database and validate retrieval quality

Usage:
    python retrieve.py                          # Run validation suite
    python retrieve.py --query "your query"     # Single query
    python retrieve.py --interactive            # Interactive mode

Features:
    - Similarity search over embeddings
    - Metadata validation
    - Content quality checks
    - Performance benchmarking
"""

# Section 1: Imports and Configuration
# Section 2: Configuration Loading
# Section 3: Qdrant Connection
# Section 4: Query Embedding Generation
# Section 5: Retrieval Function
# Section 6: Metadata Validation
# Section 7: Content Quality Checks
# Section 8: Validation Test Suite
# Section 9: Reporting and Logging
# Section 10: Main Execution
```

### 2.2 Data Flow

```
User Input (Query)
    ↓
Load Configuration (.env)
    ↓
Connect to Qdrant
    ↓
Generate Query Embedding (Cohere)
    ↓
Similarity Search (Qdrant)
    ↓
Retrieve Chunks + Metadata
    ↓
Validate Metadata Completeness
    ↓
Validate Content Quality
    ↓
Format and Display Results
    ↓
Log Validation Metrics
```

---

## 3. Detailed Component Design

### 3.1 Configuration Loading

**Objective**: Load API keys and settings from `.env`

**Implementation**:

```python
def load_configuration():
    """
    Load configuration from environment variables.

    Returns:
        dict: Configuration dictionary with all required settings

    Raises:
        ValueError: If required configuration is missing
    """
    from dotenv import load_dotenv
    import os

    load_dotenv()

    config = {
        # Required settings
        'cohere_api_key': os.getenv('COHERE_API_KEY'),
        'qdrant_url': os.getenv('QDRANT_URL'),
        'qdrant_api_key': os.getenv('QDRANT_API_KEY'),
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
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")

    return config
```

**Configuration Schema**:

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `COHERE_API_KEY` | ✅ Yes | - | Cohere API authentication |
| `QDRANT_URL` | ✅ Yes | - | Qdrant cluster URL |
| `QDRANT_API_KEY` | ✅ Yes | - | Qdrant authentication |
| `QDRANT_COLLECTION_NAME` | ❌ No | `physical_ai_book` | Collection name |
| `EMBEDDING_MODEL` | ❌ No | `embed-english-v3.0` | Cohere model |
| `DEFAULT_TOP_K` | ❌ No | `5` | Results to return |
| `MIN_RELEVANCE_SCORE` | ❌ No | `0.6` | Minimum score threshold |

### 3.2 Qdrant Connection

**Objective**: Connect to Qdrant and verify collection exists

**Implementation**:

```python
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
    """
    from qdrant_client import QdrantClient

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
            raise ValueError(
                f"Collection '{collection_name}' not found. "
                f"Available collections: {[c.name for c in collections]}"
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
```

**Validation Checks**:
- ✅ Connection successful
- ✅ Collection exists
- ✅ Collection has points (embeddings)
- ✅ Collection info accessible

### 3.3 Query Embedding Generation

**Objective**: Generate embedding for user query using Cohere

**Implementation**:

```python
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
    """
    import cohere
    import time

    try:
        start_time = time.time()

        # Initialize Cohere client
        client = cohere.Client(config['cohere_api_key'])

        # Generate embedding
        response = client.embed(
            texts=[query],
            model=config['embedding_model'],
            input_type='search_query'  # Important: different from document embedding
        )

        embedding = response.embeddings[0]
        elapsed = time.time() - start_time

        print(f"✓ Generated query embedding ({elapsed:.2f}s)")
        print(f"  Dimension: {len(embedding)}")
        print()

        return embedding

    except Exception as e:
        raise Exception(f"Failed to generate query embedding: {e}")
```

**Key Points**:
- Uses `input_type='search_query'` (not `search_document`)
- Returns 1024-dimensional vector for `embed-english-v3.0`
- Tracks embedding generation time
- Handles API errors gracefully

### 3.4 Retrieval Function

**Objective**: Search Qdrant for relevant chunks

**Implementation**:

```python
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
    """
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    import time

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
```

**Features**:
- Configurable top-K results
- Optional module filtering
- Returns full metadata payload
- Excludes vectors (not needed for validation)
- Tracks search time

### 3.5 Metadata Validation

**Objective**: Verify all metadata fields are present and valid

**Implementation**:

```python
def validate_metadata(chunks):
    """
    Validate metadata completeness and correctness.

    Args:
        chunks (list): Retrieved chunks with metadata

    Returns:
        dict: Validation results with pass/fail status
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
```

**Validation Checks**:

| Check | Validation Rule |
|-------|----------------|
| **Text** | Not empty |
| **URL** | Valid HTTP/HTTPS format |
| **Title** | Not empty |
| **Chunk ID** | Not empty |
| **Module** | Valid or None |
| **Chunk Index** | 0 ≤ index < total_chunks |
| **Score** | 0.0 ≤ score ≤ 1.0 |

### 3.6 Content Quality Validation

**Objective**: Check for HTML artifacts and text cleanliness

**Implementation**:

```python
def validate_content_quality(chunks):
    """
    Validate content quality (no HTML, clean text).

    Args:
        chunks (list): Retrieved chunks with text content

    Returns:
        dict: Quality validation results
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
        '<div', '<span',    # Common tags
        '</div>', '</span>',
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
                break  # One issue per type is enough

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
```

**Quality Checks**:
- ✅ No HTML tags (`<`, `>`, `</div>`, etc.)
- ✅ No HTML entities (`&lt;`, `&gt;`, etc.)
- ✅ No HTML attributes (`class=`, `id=`, etc.)
- ✅ No UI text ("Next", "Previous", "Edit this page")
- ✅ No excessive whitespace
- ✅ Text is not empty

### 3.7 Test Query Suite

**Objective**: Define comprehensive test queries for validation

**Implementation**:

```python
def get_test_queries():
    """
    Get predefined test queries covering various modules and query types.

    Returns:
        list: Test query definitions with expected behavior
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
```

**Query Coverage**:

| Type | Count | Purpose |
|------|-------|---------|
| **Definitional** | 2 | Test basic concept retrieval |
| **Procedural** | 1 | Test how-to queries |
| **Conceptual** | 2 | Test explanation requests |
| **Technical** | 2 | Test short/acronym queries |
| **Comparative** | 1 | Test comparison queries |

### 3.8 Validation Execution

**Objective**: Run test queries and validate results

**Implementation**:

```python
def run_validation_suite(client, config):
    """
    Run comprehensive validation suite with test queries.

    Args:
        client (QdrantClient): Connected Qdrant client
        config (dict): Configuration dictionary

    Returns:
        dict: Validation results summary
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
            chunks = retrieve_chunks(
                client,
                query_embedding,
                config,
                top_k=5
            )

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

            # Check: Module matches expected (if specified)
            if chunks and test.get('expected_modules'):
                top_module = chunks[0].get('module')
                if top_module not in test['expected_modules'] and top_module is not None:
                    query_result['issues'].append(
                        f"Top result module '{top_module}' not in expected {test['expected_modules']}"
                    )
                    # Not a hard failure, just a warning

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

### 3.9 Result Display

**Objective**: Format and display results clearly

**Implementation**:

```python
def display_retrieval_results(query, chunks, elapsed_time=None):
    """
    Display retrieval results in a formatted, readable way.

    Args:
        query (str): Original query
        chunks (list): Retrieved chunks
        elapsed_time (float, optional): Total retrieval time
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
        # Indent text
        for line in preview.split('\n'):
            print(f"    {line}")

        print()
        print("-" * 80)
        print()
```

### 3.10 Main Execution

**Objective**: Orchestrate the entire retrieval and validation flow

**Implementation**:

```python
def main():
    """
    Main execution function for retrieval and validation.
    """
    import argparse
    import sys

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

            if results['failed'] > 0:
                print("Failed Queries:")
                for qr in results['query_results']:
                    if not qr.get('passed', False):
                        print(f"  - [{qr['query_id']}] {qr['query']}")
                        if 'issues' in qr:
                            for issue in qr['issues']:
                                print(f"      {issue}")

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

                # Validate metadata
                metadata_validation = validate_metadata(chunks)
                if metadata_validation['failed'] > 0:
                    print("⚠ Metadata Issues:")
                    for issue in metadata_validation['issues']:
                        print(f"  Chunk {issue['chunk_index']}: {issue['issues']}")
                    print()

                # Validate content quality
                quality_validation = validate_content_quality(chunks)
                if quality_validation['has_issues'] > 0:
                    print("⚠ Content Quality Issues:")
                    for issue in quality_validation['issues']:
                        print(f"  Chunk {issue['chunk_index']}: {issue['issues']}")
                    print()

        elif args.query:
            # Single query mode
            import time

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
            if metadata_validation['failed'] > 0:
                print(f"  Failed: {metadata_validation['failed']}")
                for issue in metadata_validation['issues'][:3]:  # Show first 3
                    print(f"    - Chunk {issue['chunk_index']}: {', '.join(issue['issues'])}")
            print()

            print("Content Quality Validation:")
            quality_validation = validate_content_quality(chunks)
            print(f"  Clean: {quality_validation['clean']}/{quality_validation['total_chunks']}")
            if quality_validation['has_issues'] > 0:
                print(f"  Has Issues: {quality_validation['has_issues']}")
                for issue in quality_validation['issues'][:3]:  # Show first 3
                    print(f"    - Chunk {issue['chunk_index']}: {', '.join(issue['issues'])}")
            print()

        else:
            # Default: run validation
            print("No mode specified. Use --help for options.")
            print("Running validation suite by default...")
            print()

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

---

## 4. Usage Patterns

### 4.1 Validation Suite

**Command**:
```bash
python retrieve.py --validate
```

**Purpose**: Run all 8 test queries and validate retrieval quality

**Output**:
```
Loading configuration...
✓ Configuration loaded

Connecting to Qdrant...
✓ Connected to Qdrant
  Collection: physical_ai_book
  Points: 387
  Vectors: 387

================================================================================
RUNNING VALIDATION SUITE
================================================================================

[Q001] What is physical AI?
Type: definitional
Description: Basic definitional query about core concept
--------------------------------------------------------------------------------
✓ Generated query embedding (0.23s)
✓ Retrieved 5 chunks (0.31s)

✓ PASSED

Top Result:
  Score: 0.8456
  Title: Understanding Physical AI
  Module: module-01
  Preview: Physical AI combines artificial intelligence with physical systems...


[Q002] How to simulate sensors in Gazebo?
...

================================================================================
VALIDATION SUMMARY
================================================================================
Total Queries: 8
Passed: 7
Failed: 1
Pass Rate: 87.5%
```

### 4.2 Single Query

**Command**:
```bash
python retrieve.py --query "What is physical AI?"
```

**Purpose**: Test a specific query

**Output**:
```
================================================================================
QUERY: What is physical AI?
================================================================================
Total Time: 0.54s
Results: 5

[1] Score: 0.8456
    Title: Understanding Physical AI
    URL: https://site.com/docs/module-01/chapter-01
    Module: module-01
    Section: Chapter 1 > Introduction > What is Physical AI?
    Chunk: 0/12

    Text:
    Physical AI combines artificial intelligence with physical systems to create
    intelligent machines that can sense and act in the real world...

--------------------------------------------------------------------------------

Metadata Validation:
  Passed: 5/5

Content Quality Validation:
  Clean: 5/5
```

### 4.3 Interactive Mode

**Command**:
```bash
python retrieve.py --interactive
```

**Purpose**: Query multiple times in a session

**Output**:
```
Interactive Mode (type 'exit' to quit)

Query: digital twins
...
[Results displayed]

Query: sensors
...
[Results displayed]

Query: exit
```

### 4.4 Module Filtering

**Command**:
```bash
python retrieve.py --query "sensors" --module module-01
```

**Purpose**: Filter results to specific module

---

## 5. Error Handling Strategy

### 5.1 Configuration Errors

**Scenario**: Missing API keys

**Handling**:
```python
try:
    config = load_configuration()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("\nPlease ensure .env file contains:")
    print("  - COHERE_API_KEY")
    print("  - QDRANT_URL")
    print("  - QDRANT_API_KEY")
    sys.exit(1)
```

### 5.2 Connection Errors

**Scenario**: Qdrant unavailable

**Handling**:
```python
try:
    client = connect_to_qdrant(config)
except ConnectionError as e:
    print(f"Connection Error: {e}")
    print("\nPlease verify:")
    print("  - Qdrant URL is correct")
    print("  - Qdrant cluster is running")
    print("  - API key is valid")
    sys.exit(1)
```

### 5.3 Empty Results

**Scenario**: Query returns no results

**Handling**:
```python
chunks = retrieve_chunks(...)

if not chunks:
    print("⚠ No results found for this query")
    print("This could indicate:")
    print("  - Query is too specific")
    print("  - Collection is empty")
    print("  - Module filter too restrictive")
    return
```

### 5.4 API Errors

**Scenario**: Cohere API failure

**Handling**:
```python
try:
    embedding = generate_query_embedding(query, config)
except Exception as e:
    print(f"Embedding Error: {e}")
    print("\nPossible causes:")
    print("  - Invalid API key")
    print("  - Rate limit exceeded")
    print("  - Network connectivity issue")
    return None
```

---

## 6. Performance Targets

### 6.1 Latency Targets

| Operation | Target | Acceptable |
|-----------|--------|------------|
| **Configuration Load** | <0.1s | <0.5s |
| **Qdrant Connection** | <0.5s | <2s |
| **Query Embedding** | <1s | <2s |
| **Vector Search** | <0.5s | <1s |
| **Total Query** | <2s | <4s |

### 6.2 Validation Suite

**Target**: Complete 8 queries in <20 seconds

**Breakdown**:
- 8 queries × 2s avg = 16s
- Overhead: ~4s
- Total: ~20s

---

## 7. Validation Metrics

### 7.1 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Pass Rate** | ≥75% | Queries passing validation |
| **Metadata Complete** | 100% | All required fields present |
| **Content Clean** | ≥95% | No HTML artifacts |
| **Top-1 Relevance** | ≥70% | Top result is relevant |

### 7.2 Failure Modes

**Accept as Warning** (not failure):
- Module doesn't match expected (cross-module content)
- Score slightly below threshold (<0.05 difference)
- Optional fields missing (heading_hierarchy for some chunks)

**Hard Failure**:
- No results returned
- Score significantly below threshold (>0.1 difference)
- Required fields missing (text, URL, chunk_id)
- HTML artifacts detected

---

## 8. Implementation Timeline

| Task | Duration | Deliverable |
|------|----------|-------------|
| **1. Configuration & Connection** | 30 min | Config loading, Qdrant connection |
| **2. Retrieval Function** | 45 min | Query embedding, search, formatting |
| **3. Validation Functions** | 1 hour | Metadata & content validation |
| **4. Test Suite** | 45 min | Test queries, validation execution |
| **5. Display & Reporting** | 45 min | Result formatting, console output |
| **6. Main & CLI** | 45 min | Argument parsing, execution modes |
| **7. Testing & Debugging** | 1 hour | Run tests, fix issues |
| **8. Documentation** | 30 min | Docstrings, README section |
| **Total** | **6 hours** | Complete `retrieve.py` |

---

## 9. Documentation Requirements

### 9.1 Inline Documentation

**Every function must have**:
- Purpose description
- Parameter descriptions
- Return value description
- Example usage (for complex functions)
- Error handling notes

**Example**:
```python
def retrieve_chunks(client, query_embedding, config, top_k=None, module_filter=None):
    """
    Retrieve relevant chunks from Qdrant using similarity search.

    This function performs cosine similarity search over the embedded chunks
    in Qdrant and returns the top-K most relevant results with full metadata.

    Args:
        client (QdrantClient): Connected Qdrant client instance
        query_embedding (list): Query embedding vector (1024 dimensions)
        config (dict): Configuration dictionary containing collection name
        top_k (int, optional): Number of results to return. Defaults to config value.
        module_filter (str, optional): Filter results by module name (e.g., "module-01")

    Returns:
        list: List of dictionaries containing:
            - score (float): Similarity score (0.0-1.0)
            - text (str): Chunk text content
            - url (str): Source URL
            - title (str): Page title
            - module (str): Module name or None
            - heading_hierarchy (str): Breadcrumb path
            - chunk_index (int): Position in document
            - total_chunks (int): Total chunks from document
            - chunk_id (str): Unique chunk identifier

    Raises:
        Exception: If search fails or connection is lost

    Example:
        >>> chunks = retrieve_chunks(client, embedding, config, top_k=5)
        >>> print(f"Retrieved {len(chunks)} chunks")
        >>> print(f"Top score: {chunks[0]['score']:.3f}")
    """
```

### 9.2 README Section

**Add to README.md**:

````markdown
## Retrieval and Validation

### Quick Test

Test retrieval with a single query:

```bash
python retrieve.py --query "What is physical AI?"
```

### Validation Suite

Run comprehensive validation:

```bash
python retrieve.py --validate
```

This tests 8 queries covering:
- Definitional queries
- Procedural queries
- Conceptual queries
- Technical queries
- Short queries (1-2 words)
- Long queries (sentences)

### Interactive Mode

Query multiple times:

```bash
python retrieve.py --interactive
```

### Module Filtering

Filter results by module:

```bash
python retrieve.py --query "sensors" --module module-01 --top-k 10
```

### Expected Output

All validation queries should pass with:
- ✅ Results returned (5 chunks)
- ✅ Top score ≥ 0.60
- ✅ Metadata complete
- ✅ Content clean (no HTML)
````

---

## 10. Testing Checklist

### 10.1 Pre-Implementation

- [ ] `.env` file configured with valid API keys
- [ ] Qdrant collection exists and has embeddings
- [ ] Collection has ≥100 points (realistic testing)
- [ ] `config.py`, `embedder.py`, `vector_store.py` available

### 10.2 During Implementation

- [ ] Configuration loads successfully
- [ ] Qdrant connection establishes
- [ ] Query embedding generates (1024 dims)
- [ ] Vector search returns results
- [ ] Metadata validation works
- [ ] Content validation works
- [ ] Test queries execute
- [ ] Results display correctly

### 10.3 Post-Implementation

- [ ] All CLI modes work (--validate, --query, --interactive)
- [ ] Module filtering works
- [ ] Error handling graceful
- [ ] Performance meets targets (<2s per query)
- [ ] Validation suite passes (≥75%)
- [ ] Documentation complete

---

## 11. Success Criteria

### Must Have

1. ✅ Single file implementation (`retrieve.py`)
2. ✅ Configuration from `.env`
3. ✅ Qdrant connection with verification
4. ✅ Query embedding generation
5. ✅ Similarity search retrieval
6. ✅ Metadata validation
7. ✅ Content quality validation
8. ✅ 8+ test queries
9. ✅ Clear console output
10. ✅ Error handling
11. ✅ CLI argument support
12. ✅ Documentation (docstrings + README)

### Should Have

- Interactive mode
- Module filtering
- Performance metrics
- Validation summary report
- Issue logging

### Nice to Have

- JSON output mode
- CSV export
- Visual score distribution
- Comparison mode

---

## 12. Deliverables

### Code

- [ ] `retrieve.py` (single file, ~500-700 lines)

### Documentation

- [ ] Comprehensive docstrings in code
- [ ] README section explaining usage
- [ ] This plan document

### Validation

- [ ] Validation suite passes ≥75%
- [ ] Performance targets met
- [ ] All CLI modes functional

---

## Conclusion

This plan provides a complete blueprint for implementing `retrieve.py` - a single, cohesive script that:

1. **Queries** Qdrant with user input
2. **Retrieves** relevant chunks with full metadata
3. **Validates** retrieval quality and content integrity
4. **Reports** results clearly to console

The implementation follows a single-file design for simplicity while maintaining comprehensive validation capabilities. All validation logic, test queries, and reporting are self-contained in one script.

**Estimated Implementation Time**: 6 hours

**Lines of Code**: ~500-700 lines (including docstrings)

**Dependencies**: Existing modules (config, embedder, vector_store logic can be copied/adapted)

**Next Step**: Implement `retrieve.py` following this plan.
