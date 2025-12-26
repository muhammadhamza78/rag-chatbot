# Spec 2: Retrieval Pipeline Testing for RAG Chatbot

**Version**: 1.0
**Date**: December 24, 2025
**Status**: Ready for Implementation

---

## Overview

**Objective**: Validate the extraction-to-vector pipeline by testing retrieval quality, metadata accuracy, and content integrity of chunks stored in Qdrant.

**Target Audience**: Backend engineers responsible for validating the RAG data pipeline before integrating with LLMs.

**Scope**: Comprehensive testing of the retrieval layer to ensure search results are accurate, complete, and production-ready.

---

## 1. Goals and Success Criteria

### Primary Goals

1. **Retrieval Quality Validation**
   - Verify search returns semantically relevant chunks
   - Confirm ranking reflects actual relevance
   - Test diverse query types (factual, procedural, conceptual)

2. **Metadata Accuracy**
   - Ensure URL, module, heading hierarchy are correct
   - Verify chunk IDs are unique and stable
   - Confirm chunk positioning (index/total) is accurate

3. **Content Integrity**
   - Verify chunk text is clean (no HTML artifacts)
   - Confirm chunk boundaries respect semantic units
   - Ensure overlapping chunks maintain context

4. **Repeatability**
   - Same query returns consistent results
   - Results are deterministic given same embeddings
   - Pipeline handles various query types reliably

5. **Subset Testing**
   - Works with full dataset
   - Works with filtered subsets (by module)
   - Scales to different collection sizes

### Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| **Relevance** | Manual review of top-5 results | ≥80% relevant |
| **Metadata Accuracy** | All fields populated correctly | 100% |
| **Content Quality** | No HTML tags or artifacts | 100% clean |
| **Repeatability** | Same query, same results | 100% deterministic |
| **Coverage** | Queries covering all modules | All modules represented |
| **Performance** | Query response time | <2 seconds |

---

## 2. Scope and Constraints

### In Scope

✅ **Retrieval Testing**
- Query embedding generation
- Vector similarity search
- Result ranking validation
- Metadata verification
- Content quality checks

✅ **Test Coverage**
- Diverse query types
- Module-specific queries
- Edge cases (rare terms, multi-word phrases)
- Performance benchmarking

✅ **Validation Scripts**
- Automated test suite
- Manual validation tools
- Result inspection utilities
- Comparison tools

### Out of Scope

❌ **Not Building**
- LLM integration or answer generation
- Frontend chat interface
- New embedding generation (use existing)
- Production API deployment
- Authentication/authorization
- Real-time updates or caching

### Constraints

| Constraint | Details |
|------------|---------|
| **Data Source** | Use existing embeddings in Qdrant |
| **Language** | Python-only scripts |
| **Environment** | Local testing only |
| **Interface** | Console-based output |
| **Runtime** | ~Minutes per query batch |
| **Dependencies** | Existing pipeline modules |

---

## 3. Test Categories

### 3.1 Functional Tests

**Query Types to Test**:

| Query Type | Example | Expected Result |
|------------|---------|-----------------|
| **Definitional** | "What is physical AI?" | Definitions, introductions |
| **Procedural** | "How to simulate sensors?" | Step-by-step instructions |
| **Conceptual** | "Explain digital twins" | Explanations, concepts |
| **Technical** | "Gazebo physics engine" | Technical details |
| **Comparative** | "Difference between X and Y" | Comparison sections |
| **Specific Term** | "ROS" | Mentions of specific term |

**Module-Specific Queries**:
- Test queries targeting specific modules (module-01, module-02, etc.)
- Verify module filter works correctly
- Ensure cross-module queries work

**Edge Cases**:
- Rare terms (low frequency)
- Multi-word technical phrases
- Abbreviations and acronyms
- Code snippets or commands
- Very short queries (1-2 words)
- Very long queries (sentences)

### 3.2 Metadata Validation Tests

**Fields to Validate**:

```python
chunk_metadata = {
    'text': str,                    # Content validation
    'url': str,                     # URL format, accessibility
    'title': str,                   # Title presence, relevance
    'module': Optional[str],        # Module extraction accuracy
    'heading_hierarchy': str,       # Breadcrumb correctness
    'chunk_index': int,             # Position validation
    'total_chunks': int,            # Count accuracy
    'chunk_id': str,                # Uniqueness, format
}
```

**Validation Rules**:

| Field | Validation |
|-------|------------|
| `text` | Not empty, no HTML tags, readable |
| `url` | Valid URL format, matches expected domain |
| `title` | Not empty, matches page title |
| `module` | Matches URL pattern or None |
| `heading_hierarchy` | Contains valid heading path |
| `chunk_index` | 0 ≤ index < total_chunks |
| `total_chunks` | index + 1 ≤ total_chunks |
| `chunk_id` | Unique across collection, consistent format |

### 3.3 Content Quality Tests

**Checks to Perform**:

1. **HTML Artifact Detection**
   - Search for `<`, `>`, `&lt;`, `&gt;`
   - Check for `class=`, `id=`, `href=`
   - Look for navigation text ("Next", "Previous")

2. **Chunk Boundary Validation**
   - Chunks don't end mid-sentence
   - Overlapping chunks share content
   - Headings included appropriately

3. **Text Cleanliness**
   - No excessive whitespace
   - Proper line breaks
   - Special characters handled correctly

4. **Semantic Coherence**
   - Chunks make sense independently
   - Context is preserved
   - No truncated thoughts

### 3.4 Retrieval Quality Tests

**Relevance Assessment**:

| Metric | How to Measure |
|--------|----------------|
| **Precision@K** | % of top-K results that are relevant |
| **Recall** | Can we find all relevant chunks? |
| **MRR** | Mean Reciprocal Rank of first relevant result |
| **Score Distribution** | Similarity scores should be meaningful |

**Manual Review Process**:
1. Define 10-20 test queries with expected results
2. Retrieve top-5 results for each
3. Manually label as relevant/not relevant
4. Calculate precision metrics
5. Document failure cases

### 3.5 Performance Tests

**Metrics to Measure**:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Query Latency** | <2 sec | Time from query to results |
| **Embedding Time** | <1 sec | Cohere API call duration |
| **Search Time** | <0.5 sec | Qdrant search duration |
| **Total Time** | <2 sec | End-to-end query processing |

**Load Testing**:
- Single query performance
- Batch query performance (10 queries)
- Large result set (top-100)

---

## 4. Test Implementation Plan

### 4.1 Test Suite Structure

```
rag-pipeline/
├── tests/
│   ├── test_retrieval.py          # Main retrieval tests
│   ├── test_metadata.py           # Metadata validation
│   ├── test_content_quality.py    # Content quality checks
│   ├── test_performance.py        # Performance benchmarks
│   ├── test_queries.json          # Test query definitions
│   └── expected_results.json      # Expected outcomes
│
├── tools/
│   ├── inspect_results.py         # Manual result inspection
│   ├── compare_queries.py         # Query comparison tool
│   ├── validate_collection.py     # Collection validation
│   └── generate_report.py         # Test report generator
│
└── outputs/
    ├── test_results.json          # Automated test results
    ├── validation_report.md       # Human-readable report
    └── performance_metrics.csv    # Performance data
```

### 4.2 Test Query Dataset

**Structure** (`tests/test_queries.json`):

```json
{
  "queries": [
    {
      "id": "Q001",
      "query": "What is physical AI?",
      "type": "definitional",
      "expected_modules": ["module-01"],
      "expected_keywords": ["physical AI", "intelligent systems", "sensors"],
      "min_relevance_score": 0.7
    },
    {
      "id": "Q002",
      "query": "How to simulate sensors in Gazebo?",
      "type": "procedural",
      "expected_modules": ["module-02"],
      "expected_keywords": ["Gazebo", "sensor", "simulation"],
      "min_relevance_score": 0.65
    }
  ]
}
```

**Query Categories** (Minimum 20 queries):
- 5 definitional queries
- 5 procedural queries
- 5 conceptual queries
- 3 technical queries
- 2 comparative queries
- Variable query lengths and complexities

### 4.3 Automated Test Script

**Core Test Functions**:

```python
def test_retrieval_returns_results():
    """Test that queries return non-empty results."""
    for query in test_queries:
        results = retrieve(query['query'])
        assert len(results) > 0, f"No results for: {query['query']}"

def test_metadata_completeness():
    """Test that all metadata fields are populated."""
    results = retrieve(sample_query)
    for result in results:
        assert result.get('text'), "Missing text"
        assert result.get('url'), "Missing URL"
        assert result.get('chunk_id'), "Missing chunk_id"

def test_content_has_no_html():
    """Test that content is clean (no HTML tags)."""
    results = retrieve_all_samples()
    for result in results:
        text = result['text']
        assert '<' not in text, f"HTML found in: {result['chunk_id']}"
        assert 'class=' not in text, f"HTML attribute found"

def test_chunk_boundaries():
    """Test that chunks respect sentence boundaries."""
    results = retrieve(sample_query)
    for result in results:
        text = result['text'].strip()
        # Check doesn't end mid-word
        assert text[-1] in '.!?"\n', f"Bad ending: {text[-50:]}"

def test_relevance_scores():
    """Test that relevance scores are in valid range."""
    results = retrieve(sample_query)
    for result in results:
        score = result['score']
        assert 0.0 <= score <= 1.0, f"Invalid score: {score}"

def test_module_filtering():
    """Test that module filtering works correctly."""
    results = retrieve(query, module_filter="module-01")
    for result in results:
        module = result.get('module')
        assert module == "module-01" or module is None

def test_deterministic_results():
    """Test that same query returns same results."""
    results1 = retrieve(query)
    results2 = retrieve(query)
    assert results1 == results2, "Non-deterministic results"
```

### 4.4 Manual Validation Tools

**Result Inspector** (`tools/inspect_results.py`):

```python
"""
Interactive tool for manual result inspection.

Usage:
    python inspect_results.py "What is physical AI?"

Output:
    Formatted results with:
    - Relevance scores
    - Full metadata
    - Text snippets with highlighting
    - Side-by-side comparison
"""
```

**Query Comparator** (`tools/compare_queries.py`):

```python
"""
Compare results from different queries.

Usage:
    python compare_queries.py "physical AI" "intelligent systems"

Output:
    Venn diagram (text-based) showing:
    - Unique results for query 1
    - Unique results for query 2
    - Overlapping results
"""
```

**Collection Validator** (`tools/validate_collection.py`):

```python
"""
Validate entire Qdrant collection.

Checks:
    - Total point count
    - Metadata completeness
    - Chunk ID uniqueness
    - URL distribution
    - Module distribution
"""
```

---

## 5. Validation Workflow

### Step 1: Pre-Test Validation

**Verify Collection State**:
```bash
python tools/validate_collection.py
```

**Expected Output**:
```
Collection Validation Report
============================
Collection: physical_ai_book
Total Points: 387
Vector Dimension: 1024
Distance Metric: Cosine

Metadata Completeness:
  - text: 387/387 (100%)
  - url: 387/387 (100%)
  - chunk_id: 387/387 (100%)
  - module: 305/387 (78.8%)  ← Some chunks may not have module

Chunk ID Uniqueness: ✓ All unique
URL Distribution:
  - Total unique URLs: 50
  - Chunks per URL: avg=7.7, min=3, max=15

Module Distribution:
  - module-01: 98 chunks
  - module-02: 102 chunks
  - module-03: 56 chunks
  - module-04: 49 chunks
  - None: 82 chunks (intro, glossary, etc.)

✓ Collection is healthy and ready for testing
```

### Step 2: Run Automated Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test category
python -m pytest tests/test_retrieval.py -v

# Generate test report
python tools/generate_report.py
```

**Expected Test Output**:
```
tests/test_retrieval.py::test_retrieval_returns_results PASSED
tests/test_retrieval.py::test_relevance_scores PASSED
tests/test_retrieval.py::test_module_filtering PASSED
tests/test_retrieval.py::test_deterministic_results PASSED

tests/test_metadata.py::test_metadata_completeness PASSED
tests/test_metadata.py::test_chunk_id_uniqueness PASSED
tests/test_metadata.py::test_url_validity PASSED

tests/test_content_quality.py::test_content_has_no_html PASSED
tests/test_content_quality.py::test_chunk_boundaries PASSED
tests/test_content_quality.py::test_text_cleanliness PASSED

tests/test_performance.py::test_query_latency PASSED
tests/test_performance.py::test_batch_queries PASSED

======================== 12 passed in 45.3s ========================
```

### Step 3: Manual Validation

**Inspect Sample Results**:
```bash
python tools/inspect_results.py "What is physical AI?"
```

**Review Output**:
```
Query: "What is physical AI?"
Query Embedding: [1024 dimensions] (0.023s)
Search Time: 0.31s
Total Time: 0.33s

Results (Top 5):
================================================================================
[1] Score: 0.8456
    URL: https://site.com/docs/module-01/chapter-01-understanding-physical-ai
    Module: module-01
    Title: Understanding Physical AI
    Section: Chapter 1 > Introduction > What is Physical AI?
    Chunk: 0/12

    Text (first 200 chars):
    Physical AI combines artificial intelligence with physical systems to create
    intelligent machines that can sense and act in the real world. Unlike pure
    software AI, physical AI must deal...

    ✓ Relevant: Yes
    ✓ Clean text: Yes
    ✓ Metadata complete: Yes
================================================================================
[2] Score: 0.8123
    ...
```

### Step 4: Compare Queries

```bash
python tools/compare_queries.py "physical AI" "intelligent systems" "robotics"
```

**Output**: Shows overlap and differences in retrieved chunks

### Step 5: Generate Report

```bash
python tools/generate_report.py --output outputs/validation_report.md
```

**Report Contents**:
1. Executive summary
2. Collection statistics
3. Test results (pass/fail)
4. Relevance analysis
5. Performance metrics
6. Issue log
7. Recommendations

---

## 6. Test Cases (Examples)

### 6.1 Basic Retrieval Tests

**Test Case 1: Simple Definitional Query**
```python
query = "What is physical AI?"
expected = {
    'min_results': 3,
    'min_score': 0.6,
    'expected_modules': ['module-01'],
    'must_contain_keywords': ['physical AI', 'intelligent'],
}
```

**Test Case 2: Technical Query**
```python
query = "How does Gazebo simulate physics?"
expected = {
    'min_results': 3,
    'min_score': 0.6,
    'expected_modules': ['module-02'],
    'must_contain_keywords': ['Gazebo', 'physics', 'simulation'],
}
```

**Test Case 3: Module-Filtered Query**
```python
query = "sensors"
module_filter = "module-01"
expected = {
    'min_results': 2,
    'all_results_have_module': 'module-01',
}
```

### 6.2 Edge Case Tests

**Test Case 4: Very Short Query**
```python
query = "ROS"
expected = {
    'min_results': 1,  # Should still return results
    'tolerance': 'lower_scores_acceptable',
}
```

**Test Case 5: Long Query**
```python
query = "Explain the process of creating a digital twin of a robotic system using Gazebo for physics simulation and Unity for rendering"
expected = {
    'min_results': 3,
    'should_cover_multiple_concepts': ['digital twin', 'Gazebo', 'Unity'],
}
```

**Test Case 6: Rare Term**
```python
query = "lidar point cloud processing"
expected = {
    'min_results': 1,
    'may_have_lower_scores': True,
}
```

### 6.3 Content Quality Tests

**Test Case 7: No HTML Artifacts**
```python
def test_no_html():
    results = retrieve_sample(n=50)
    for result in results:
        assert_no_html_tags(result['text'])
        assert_no_navigation_text(result['text'])
        assert_no_ui_elements(result['text'])
```

**Test Case 8: Chunk Overlap Validation**
```python
def test_chunk_overlap():
    # Get consecutive chunks from same document
    chunks = get_chunks_from_url(url, limit=3)
    chunk1, chunk2 = chunks[0], chunks[1]

    # Check for expected overlap (~100 words)
    overlap = calculate_overlap(chunk1['text'], chunk2['text'])
    assert 50 <= overlap <= 150, f"Overlap {overlap} words out of range"
```

### 6.4 Performance Tests

**Test Case 9: Query Latency**
```python
def test_query_latency():
    queries = get_test_queries()
    latencies = []

    for query in queries:
        start = time.time()
        results = retrieve(query)
        latency = time.time() - start
        latencies.append(latency)

    avg_latency = sum(latencies) / len(latencies)
    assert avg_latency < 2.0, f"Average latency {avg_latency}s exceeds 2s"
```

**Test Case 10: Batch Performance**
```python
def test_batch_queries():
    queries = get_test_queries(n=10)

    start = time.time()
    results = [retrieve(q) for q in queries]
    total_time = time.time() - start

    assert total_time < 20.0, f"Batch time {total_time}s exceeds 20s"
```

---

## 7. Expected Outputs

### 7.1 Test Results Summary

**File**: `outputs/test_results.json`

```json
{
  "timestamp": "2025-12-24T23:30:00Z",
  "collection": "physical_ai_book",
  "total_points": 387,
  "tests_run": 12,
  "tests_passed": 12,
  "tests_failed": 0,
  "pass_rate": 100.0,
  "categories": {
    "retrieval": {"passed": 4, "failed": 0},
    "metadata": {"passed": 3, "failed": 0},
    "content_quality": {"passed": 3, "failed": 0},
    "performance": {"passed": 2, "failed": 0}
  },
  "query_performance": {
    "avg_latency": 0.35,
    "min_latency": 0.22,
    "max_latency": 0.51,
    "p95_latency": 0.48
  }
}
```

### 7.2 Validation Report

**File**: `outputs/validation_report.md`

```markdown
# RAG Retrieval Pipeline Validation Report

**Date**: December 24, 2025
**Collection**: physical_ai_book
**Test Status**: ✅ PASSED

## Executive Summary

All 12 automated tests passed successfully. Manual validation of 20 test queries
shows 85% relevance rate (target: ≥80%). Content quality is excellent with no
HTML artifacts detected. Performance meets targets with average query latency
of 0.35s (target: <2s).

## Collection Statistics

- Total Points: 387
- Vector Dimension: 1024
- Unique URLs: 50
- Modules Represented: 4 + general content

## Test Results

### Retrieval Tests (4/4 passed)
✅ Queries return non-empty results
✅ Relevance scores in valid range
✅ Module filtering works correctly
✅ Results are deterministic

### Metadata Tests (3/3 passed)
✅ All required fields populated
✅ Chunk IDs are unique
✅ URLs are valid format

### Content Quality Tests (3/3 passed)
✅ No HTML artifacts detected
✅ Chunk boundaries respect sentences
✅ Text is clean and readable

### Performance Tests (2/2 passed)
✅ Query latency < 2s
✅ Batch query performance acceptable

## Relevance Analysis

Manual review of 20 queries × 5 results = 100 results:
- Relevant: 85 (85%)
- Partially Relevant: 10 (10%)
- Not Relevant: 5 (5%)

**Exceeds target of ≥80% relevance**

## Performance Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Avg Latency | 0.35s | <2s | ✅ Pass |
| P95 Latency | 0.48s | <3s | ✅ Pass |
| Batch (10 queries) | 3.8s | <20s | ✅ Pass |

## Issues Found

None

## Recommendations

1. ✅ Pipeline is production-ready for retrieval
2. Consider adding reranking for improved relevance
3. Monitor performance as collection grows
```

### 7.3 Performance Metrics

**File**: `outputs/performance_metrics.csv`

```csv
query_id,query,embedding_time_ms,search_time_ms,total_time_ms,result_count,top_score
Q001,What is physical AI?,23,310,333,5,0.8456
Q002,How to simulate sensors?,25,295,320,5,0.8123
Q003,Explain digital twins,22,315,337,5,0.7891
...
```

---

## 8. Acceptance Criteria

### 8.1 Functional Requirements

| Requirement | Acceptance |
|-------------|------------|
| ✅ Search returns results | All test queries return ≥1 result |
| ✅ Results are relevant | ≥80% of top-5 results are relevant (manual review) |
| ✅ Metadata is complete | 100% of required fields populated |
| ✅ Content is clean | 0 HTML artifacts detected |
| ✅ Module filtering works | Filter returns only specified module |
| ✅ Results are deterministic | Same query returns identical results |

### 8.2 Quality Requirements

| Requirement | Acceptance |
|-------------|------------|
| ✅ No HTML in text | 100% clean content |
| ✅ Valid URLs | All URLs match expected format |
| ✅ Unique chunk IDs | No duplicates across collection |
| ✅ Proper chunk boundaries | Chunks end at sentence boundaries |
| ✅ Overlap maintained | Consecutive chunks share ~100 words |

### 8.3 Performance Requirements

| Requirement | Target | Acceptance |
|-------------|--------|------------|
| ✅ Query latency | <2s | Average <2s, P95 <3s |
| ✅ Embedding time | <1s | Cohere API <1s |
| ✅ Search time | <0.5s | Qdrant search <0.5s |
| ✅ Batch queries (10) | <20s | Total time <20s |

---

## 9. Dependencies and Prerequisites

### 9.1 Prerequisites

**Must Be Complete**:
- ✅ Spec 1 implementation (ingestion pipeline)
- ✅ Qdrant collection populated with embeddings
- ✅ Collection contains ≥100 chunks (realistic testing)

**Required Access**:
- Cohere API key (for query embeddings)
- Qdrant cluster access
- Existing collection name

### 9.2 Dependencies

**Python Packages**:
```txt
# From existing pipeline
cohere==5.12.1
qdrant-client==1.12.0
python-dotenv==1.0.1

# New for testing
pytest==7.4.3
pytest-benchmark==4.0.0
tabulate==0.9.0
```

**Existing Modules**:
- `config.py` - Configuration
- `embedder.py` - Query embedding
- `vector_store.py` - Qdrant search
- `search.py` - Search utility (can be extended)

---

## 10. Implementation Timeline

| Phase | Task | Duration | Deliverable |
|-------|------|----------|-------------|
| 1 | Test query dataset creation | 1 hour | test_queries.json |
| 2 | Automated test suite | 2 hours | tests/*.py |
| 3 | Manual validation tools | 2 hours | tools/*.py |
| 4 | Collection validator | 1 hour | validate_collection.py |
| 5 | Test execution & review | 1 hour | Test results |
| 6 | Report generation | 1 hour | validation_report.md |
| **Total** | | **8 hours** | Complete test suite |

---

## 11. Deliverables Checklist

### Code Deliverables

- [ ] `tests/test_retrieval.py` - Core retrieval tests
- [ ] `tests/test_metadata.py` - Metadata validation
- [ ] `tests/test_content_quality.py` - Content quality tests
- [ ] `tests/test_performance.py` - Performance benchmarks
- [ ] `tests/test_queries.json` - Test query dataset
- [ ] `tools/inspect_results.py` - Manual inspection tool
- [ ] `tools/compare_queries.py` - Query comparison
- [ ] `tools/validate_collection.py` - Collection validation
- [ ] `tools/generate_report.py` - Report generator

### Documentation Deliverables

- [ ] `SPEC_2_RETRIEVAL_TESTING.md` - This specification
- [ ] `TESTING_GUIDE.md` - How to run tests
- [ ] `outputs/validation_report.md` - Test results report

### Output Deliverables

- [ ] `outputs/test_results.json` - Automated test results
- [ ] `outputs/performance_metrics.csv` - Performance data
- [ ] `outputs/validation_report.md` - Summary report

---

## 12. Success Metrics

**Pipeline is validated when**:

1. ✅ All automated tests pass (12/12)
2. ✅ Manual relevance review ≥80%
3. ✅ No critical issues found
4. ✅ Performance targets met
5. ✅ Documentation complete
6. ✅ Report generated and reviewed

**Ready for next phase when**:
- Retrieval quality is confirmed
- Metadata accuracy is verified
- Performance is acceptable
- Edge cases are handled
- Documentation is complete

---

## Appendix A: Sample Test Queries

**Definitional Queries**:
1. What is physical AI?
2. Define digital twin
3. What are sensors in robotics?
4. Explain embodied AI
5. What is a simulation environment?

**Procedural Queries**:
1. How to simulate sensors in Gazebo?
2. How to create a digital twin?
3. Steps to integrate ROS with Unity
4. How to validate sensor data?
5. Process for physics simulation

**Conceptual Queries**:
1. Explain the role of sensors in physical AI
2. Relationship between digital twins and simulation
3. Why use Gazebo for robotics?
4. Benefits of physics simulation
5. Importance of rendering in digital twins

**Technical Queries**:
1. Gazebo physics engine configuration
2. ROS sensor message types
3. Unity rendering pipeline
4. LIDAR point cloud processing
5. Camera sensor calibration

**Comparative Queries**:
1. Difference between Gazebo and Unity
2. Real sensors vs simulated sensors
3. Physics simulation vs kinematics

---

## Appendix B: Validation Rubric

**Relevance Scoring** (Manual Review):

| Score | Label | Criteria |
|-------|-------|----------|
| 2 | Highly Relevant | Directly answers query, on-topic |
| 1 | Partially Relevant | Related but indirect |
| 0 | Not Relevant | Off-topic or unrelated |

**Content Quality Scoring**:

| Aspect | Good (2) | Acceptable (1) | Poor (0) |
|--------|----------|----------------|----------|
| Cleanliness | No HTML, clean text | Minor formatting issues | HTML artifacts |
| Readability | Clear, coherent | Understandable | Confusing |
| Completeness | Full context | Partial context | Truncated |

**Metadata Quality Scoring**:

| Field | Valid (1) | Invalid (0) |
|-------|-----------|-------------|
| URL | Correct format, accessible | Malformed or broken |
| Module | Matches URL or None | Incorrect |
| Heading | Valid breadcrumb | Empty or garbled |
| Chunk ID | Unique, consistent | Duplicate or missing |

---

## Conclusion

This specification defines a comprehensive testing strategy for validating the RAG retrieval pipeline. By following this spec, backend engineers can ensure the ingestion pipeline produces high-quality, retrievable data ready for LLM integration.

**Next Steps After Validation**:
1. Address any issues found during testing
2. Optimize query performance if needed
3. Prepare for Spec 3 (LLM integration)
4. Document lessons learned
