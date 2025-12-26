# Spec 2 Implementation Plan - Quick Summary

**Goal**: Build `retrieve.py` - a single Python script for retrieval and validation

---

## 🎯 **What We're Building**

A **single-file** Python script (`retrieve.py`) that:
- Queries Qdrant vector database
- Retrieves relevant chunks
- Validates metadata and content quality
- Runs comprehensive test suite
- Provides clear console output

---

## 📋 **Core Components** (in one file)

| Section | Purpose | Lines |
|---------|---------|-------|
| **1. Configuration** | Load `.env` settings | ~50 |
| **2. Connection** | Connect to Qdrant | ~40 |
| **3. Embedding** | Generate query embeddings | ~35 |
| **4. Retrieval** | Search and retrieve chunks | ~60 |
| **5. Metadata Validation** | Check metadata completeness | ~70 |
| **6. Content Validation** | Check for HTML, quality | ~70 |
| **7. Test Suite** | 8 predefined test queries | ~80 |
| **8. Display** | Format and show results | ~50 |
| **9. Main** | CLI and execution modes | ~100 |

**Total**: ~500-700 lines in `retrieve.py`

---

## 🔧 **Three Usage Modes**

### 1. Validation Suite (Default)
```bash
python retrieve.py --validate
```
Runs 8 test queries and validates retrieval quality

### 2. Single Query
```bash
python retrieve.py --query "What is physical AI?"
```
Test a specific query with full validation

### 3. Interactive
```bash
python retrieve.py --interactive
```
Multiple queries in one session

---

## ✅ **Validation Checks**

### **Metadata Validation** (100% target)
- ✅ All required fields present (text, URL, title, chunk_id)
- ✅ Valid URL format
- ✅ Chunk index in valid range
- ✅ Score between 0.0 and 1.0

### **Content Quality** (95%+ target)
- ✅ No HTML tags (`<`, `>`, `</div>`)
- ✅ No HTML attributes (`class=`, `id=`)
- ✅ No UI text ("Next", "Previous")
- ✅ No excessive whitespace
- ✅ Text not empty

### **Retrieval Quality** (75%+ target)
- ✅ Results returned
- ✅ Top score ≥ minimum threshold
- ✅ Expected keywords present
- ✅ Module matches expected

---

## 🧪 **Test Query Suite** (8 queries)

| ID | Query | Type | Purpose |
|----|-------|------|---------|
| Q001 | "What is physical AI?" | Definitional | Core concept |
| Q002 | "How to simulate sensors in Gazebo?" | Procedural | How-to query |
| Q003 | "Explain digital twins" | Conceptual | Explanation |
| Q004 | "What are sensors in robotics?" | Definitional | Cross-module |
| Q005 | "Unity rendering" | Technical | Short query (2 words) |
| Q006 | "How does physics simulation work?" | Conceptual | Long query |
| Q007 | "ROS" | Technical | Very short (1 word) |
| Q008 | "Difference between simulation and real" | Comparative | Comparison |

---

## 📊 **Expected Output**

### Validation Suite
```
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
  Preview: Physical AI combines artificial intelligence...

...

================================================================================
VALIDATION SUMMARY
================================================================================
Total Queries: 8
Passed: 7
Failed: 1
Pass Rate: 87.5%
```

### Single Query
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
    Section: Chapter 1 > Introduction

    Text:
    Physical AI combines artificial intelligence with physical systems...

Metadata Validation:
  Passed: 5/5

Content Quality Validation:
  Clean: 5/5
```

---

## ⏱️ **Performance Targets**

| Operation | Target | Acceptable |
|-----------|--------|------------|
| Query embedding | <1s | <2s |
| Vector search | <0.5s | <1s |
| **Total per query** | **<2s** | **<4s** |
| **Full suite (8 queries)** | **<20s** | **<30s** |

---

## 🔍 **Function Breakdown**

### Core Functions

```python
def load_configuration():
    """Load .env settings and validate"""

def connect_to_qdrant(config):
    """Connect to Qdrant and verify collection"""

def generate_query_embedding(query, config):
    """Generate query embedding with Cohere"""

def retrieve_chunks(client, query_embedding, config, top_k, module_filter):
    """Search Qdrant and retrieve chunks"""

def validate_metadata(chunks):
    """Check metadata completeness and validity"""

def validate_content_quality(chunks):
    """Check for HTML artifacts and text quality"""

def get_test_queries():
    """Return 8 predefined test queries"""

def run_validation_suite(client, config):
    """Execute all test queries and validate"""

def display_retrieval_results(query, chunks, elapsed_time):
    """Format and display results"""

def main():
    """CLI and execution orchestration"""
```

---

## 📝 **Implementation Checklist**

### Step 1: Configuration (30 min)
- [ ] Load `.env` with `python-dotenv`
- [ ] Validate required settings
- [ ] Provide clear error messages

### Step 2: Connection (45 min)
- [ ] Connect to Qdrant
- [ ] Verify collection exists
- [ ] Check collection has points

### Step 3: Retrieval (1 hour)
- [ ] Generate query embeddings
- [ ] Perform similarity search
- [ ] Format results with metadata

### Step 4: Validation (1.5 hours)
- [ ] Metadata validation function
- [ ] Content quality validation
- [ ] Test query definitions

### Step 5: Display & CLI (1.5 hours)
- [ ] Result formatting
- [ ] CLI argument parsing
- [ ] Three execution modes

### Step 6: Testing (1 hour)
- [ ] Test all CLI modes
- [ ] Verify validation logic
- [ ] Check error handling

### Step 7: Documentation (30 min)
- [ ] Add docstrings
- [ ] Update README
- [ ] Create usage examples

**Total**: ~6 hours

---

## ✨ **Key Features**

1. **Single File** - Everything in `retrieve.py`
2. **Self-Contained** - Minimal external dependencies
3. **Comprehensive** - Full validation suite built-in
4. **Flexible** - Three usage modes (validate, query, interactive)
5. **Clear Output** - Human-readable console formatting
6. **Error Handling** - Graceful failures with helpful messages

---

## 🎯 **Success Criteria**

**Must Pass**:
- ✅ Validation suite ≥75% pass rate
- ✅ Metadata 100% complete
- ✅ Content 95%+ clean
- ✅ Performance <2s per query
- ✅ All CLI modes work
- ✅ Clear documentation

---

## 📚 **Documentation**

**Full Plan**: `PLAN_SPEC2_RETRIEVE.md` (12,000 words)
- Detailed component design
- Complete function implementations
- Usage patterns
- Error handling strategy
- Testing checklist

**This Summary**: Quick reference for implementation

---

## 🚀 **Next Steps**

1. **Review Plan**: Read `PLAN_SPEC2_RETRIEVE.md`
2. **Implement**: Build `retrieve.py` following the plan
3. **Test**: Run validation suite
4. **Document**: Update README with usage

---

**Estimated Time**: 6 hours for complete implementation

**Deliverable**: Single `retrieve.py` file (~500-700 lines)

**Dependencies**: Existing config, embedder, vector_store logic (can be adapted/copied)
