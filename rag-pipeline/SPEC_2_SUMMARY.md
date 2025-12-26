# Spec 2 Summary: Retrieval Pipeline Testing

**Quick Reference for Backend Engineers**

---

## 🎯 **What Is This?**

Spec 2 defines comprehensive testing of the RAG retrieval pipeline to validate:
- ✅ Search results are relevant and accurate
- ✅ Metadata is correct and complete
- ✅ Content quality is high (no HTML, proper chunking)
- ✅ Performance meets targets (<2s per query)

---

## 📋 **What We're Testing**

### **1. Retrieval Quality** (80%+ relevance target)
- Do queries return relevant chunks?
- Are results properly ranked by relevance?
- Do different query types work well?

### **2. Metadata Accuracy** (100% target)
- Are URLs correct?
- Is module extraction accurate?
- Are chunk IDs unique?
- Is heading hierarchy preserved?

### **3. Content Integrity** (100% target)
- No HTML artifacts
- No UI text (navigation, buttons)
- Proper chunk boundaries
- Clean, readable text

### **4. Performance** (<2s target)
- Query latency
- Embedding generation time
- Qdrant search time

---

## 🧪 **Test Categories**

| Category | Tests | Purpose |
|----------|-------|---------|
| **Functional** | 4 tests | Basic retrieval works |
| **Metadata** | 3 tests | All fields accurate |
| **Content Quality** | 3 tests | Clean, readable text |
| **Performance** | 2 tests | Fast enough for production |

**Total**: 12 automated tests + manual validation

---

## 📝 **Test Query Types**

We'll test with 20+ queries covering:

| Type | Example | Expected |
|------|---------|----------|
| **Definitional** | "What is physical AI?" | Definitions, intro content |
| **Procedural** | "How to simulate sensors?" | Step-by-step instructions |
| **Conceptual** | "Explain digital twins" | Explanations, theory |
| **Technical** | "Gazebo physics engine" | Technical details |
| **Comparative** | "Difference between X and Y" | Comparison sections |

---

## 🛠️ **What We'll Build**

### **Automated Tests**
```
tests/
├── test_retrieval.py          # Core search tests
├── test_metadata.py           # Metadata validation
├── test_content_quality.py    # Content checks
├── test_performance.py        # Speed benchmarks
└── test_queries.json          # Test dataset
```

### **Manual Validation Tools**
```
tools/
├── inspect_results.py         # Interactive result viewer
├── compare_queries.py         # Query comparison
├── validate_collection.py     # Collection health check
└── generate_report.py         # Report generator
```

### **Outputs**
```
outputs/
├── test_results.json          # Automated test results
├── performance_metrics.csv    # Performance data
└── validation_report.md       # Human-readable report
```

---

## ✅ **Success Criteria**

**All must pass**:

1. ✅ All 12 automated tests pass
2. ✅ ≥80% of results are relevant (manual review)
3. ✅ 100% metadata completeness
4. ✅ 0 HTML artifacts in content
5. ✅ Average query latency <2 seconds
6. ✅ Results are deterministic (same query → same results)

---

## 🚀 **How to Run Tests**

```bash
# 1. Validate collection first
python tools/validate_collection.py

# 2. Run automated tests
python -m pytest tests/ -v

# 3. Manual inspection
python tools/inspect_results.py "What is physical AI?"

# 4. Compare queries
python tools/compare_queries.py "sensors" "actuators"

# 5. Generate report
python tools/generate_report.py
```

---

## 📊 **Expected Results**

### **Automated Tests**
```
tests/test_retrieval.py .................. PASSED (4/4)
tests/test_metadata.py ................... PASSED (3/3)
tests/test_content_quality.py ............ PASSED (3/3)
tests/test_performance.py ................ PASSED (2/2)

======================== 12 passed in 45s ========================
```

### **Performance**
- Avg latency: ~0.35s (target: <2s) ✅
- P95 latency: ~0.48s (target: <3s) ✅
- Batch (10 queries): ~3.8s (target: <20s) ✅

### **Relevance**
- 85% relevant (target: ≥80%) ✅
- 10% partially relevant
- 5% not relevant

---

## 🎯 **Key Validations**

### **Query: "What is physical AI?"**

**Expected Top Result**:
```
[1] Score: 0.85
    URL: .../docs/module-01/chapter-01-understanding-physical-ai
    Module: module-01
    Title: Understanding Physical AI
    Section: Chapter 1 > Introduction > What is Physical AI?

    Text:
    Physical AI combines artificial intelligence with physical
    systems to create intelligent machines that can sense and
    act in the real world...

    ✓ Relevant
    ✓ Clean text
    ✓ Metadata complete
```

### **Metadata Validation**

All results must have:
- ✅ `text`: Non-empty, no HTML
- ✅ `url`: Valid format
- ✅ `title`: Page title present
- ✅ `module`: Correct or None
- ✅ `heading_hierarchy`: Breadcrumb path
- ✅ `chunk_id`: Unique identifier
- ✅ `chunk_index`: Position in document
- ✅ `score`: Between 0.0 and 1.0

---

## 📦 **Deliverables**

### **Code** (9 files)
- 4 test modules
- 4 validation tools
- 1 test dataset

### **Documentation** (2 files)
- Full specification (SPEC_2_RETRIEVAL_TESTING.md)
- Testing guide (TESTING_GUIDE.md)

### **Reports** (3 files)
- Automated test results (JSON)
- Performance metrics (CSV)
- Validation report (Markdown)

---

## ⏱️ **Timeline**

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Test dataset | 1 hour | test_queries.json |
| Automated tests | 2 hours | tests/*.py |
| Validation tools | 2 hours | tools/*.py |
| Collection validator | 1 hour | validate_collection.py |
| Execution & review | 1 hour | Results |
| Report generation | 1 hour | Report |
| **Total** | **8 hours** | Complete suite |

---

## 🔍 **Sample Test Cases**

### **Test 1: Basic Retrieval**
```python
def test_query_returns_results():
    results = retrieve("What is physical AI?")
    assert len(results) > 0
    assert results[0]['score'] > 0.6
```

### **Test 2: Metadata Complete**
```python
def test_metadata_complete():
    results = retrieve("digital twins")
    for r in results:
        assert r.get('url')
        assert r.get('chunk_id')
        assert r.get('text')
```

### **Test 3: No HTML**
```python
def test_no_html_artifacts():
    results = retrieve_sample(n=50)
    for r in results:
        assert '<' not in r['text']
        assert 'class=' not in r['text']
```

### **Test 4: Performance**
```python
def test_query_latency():
    start = time.time()
    results = retrieve("sensors")
    latency = time.time() - start
    assert latency < 2.0
```

---

## 🎓 **What This Enables**

After successful validation:

1. ✅ **Confidence** in data quality
2. ✅ **Proof** retrieval works correctly
3. ✅ **Baseline** for performance
4. ✅ **Documentation** for future work
5. ✅ **Ready** for LLM integration (Spec 3)

---

## 🚫 **What We're NOT Building**

- ❌ LLM integration
- ❌ Frontend chat interface
- ❌ New embedding generation
- ❌ Production API
- ❌ Authentication
- ❌ Real-time updates

**Focus**: Validate existing retrieval pipeline only

---

## 📚 **Documentation**

**Full Spec**: `SPEC_2_RETRIEVAL_TESTING.md` (15,000 words)
- Detailed test categories
- Implementation plan
- Expected outputs
- Acceptance criteria
- Sample test cases

**Testing Guide**: `TESTING_GUIDE.md` (coming soon)
- Step-by-step instructions
- Interpreting results
- Troubleshooting

---

## ✨ **Quick Start**

```bash
# 1. Ensure Spec 1 is complete
# (Qdrant collection populated)

# 2. Install test dependencies
pip install pytest pytest-benchmark tabulate

# 3. Run validation
python tools/validate_collection.py

# 4. Run tests
python -m pytest tests/ -v

# 5. Review report
cat outputs/validation_report.md
```

---

## 📞 **Questions?**

Refer to:
- Full specification: `SPEC_2_RETRIEVAL_TESTING.md`
- Spec 1 docs: `README.md`, `ARCHITECTURE.md`
- Implementation guide: `TESTING_GUIDE.md` (to be created)

---

**Status**: ✅ Specification complete and ready for implementation

**Dependencies**: Requires Spec 1 (ingestion pipeline) to be complete

**Next**: Implement test suite as defined in full specification
