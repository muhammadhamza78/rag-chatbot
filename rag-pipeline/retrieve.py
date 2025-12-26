#!/usr/bin/env python3
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

import os
import sys
import time
import argparse
from dotenv import load_dotenv
import cohere
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue


# ============================================================================
# CONFIGURATION
# ============================================================================

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


# ============================================================================
# QDRANT CONNECTION
# ============================================================================

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


# ============================================================================
# QUERY EMBEDDING GENERATION
# ============================================================================

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


# ============================================================================
# RETRIEVAL FUNCTION
# ============================================================================

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

        # Handle empty results
        if not results:
            print("⚠ No results found for this query")
            print("This could indicate:")
            print("  - Query is too specific")
            print("  - Collection is empty")
            print("  - Module filter too restrictive")
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


# ============================================================================
# METADATA VALIDATION
# ============================================================================

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


# ============================================================================
# CONTENT QUALITY VALIDATION
# ============================================================================

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


# ============================================================================
# TEST QUERY SUITE
# ============================================================================

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


# ============================================================================
# VALIDATION EXECUTION
# ============================================================================

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
                text_preview = chunks[0]['text'][:150]
                if len(chunks[0]['text']) > 150:
                    text_preview += "..."
                print(f"  Preview: {text_preview}")

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


# ============================================================================
# RESULT DISPLAY
# ============================================================================

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


# ============================================================================
# MAIN EXECUTION
# ============================================================================

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

            if results['failed'] > 0:
                print("Failed Queries:")
                for qr in results['query_results']:
                    if not qr.get('passed', False):
                        print(f"  - [{qr['query_id']}] {qr['query']}")
                        if 'issues' in qr:
                            for issue in qr['issues']:
                                print(f"      {issue}")
                        if 'error' in qr:
                            print(f"      Error: {qr['error']}")

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
                        print(f"  Chunk {issue['chunk_index']}: {', '.join(issue['issues'])}")
                    print()

                # Validate content quality
                quality_validation = validate_content_quality(chunks)
                if quality_validation['has_issues'] > 0:
                    print("⚠ Content Quality Issues:")
                    for issue in quality_validation['issues']:
                        print(f"  Chunk {issue['chunk_index']}: {', '.join(issue['issues'])}")
                    print()

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
            print("No mode specified. Running validation suite...")
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
