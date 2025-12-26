# RAG Agent Quick Start Guide

Get started with the Physical AI RAG Agent in 5 minutes.

---

## Prerequisites

- Python 3.8+
- Completed Spec 1 (Qdrant collection populated)
- OpenAI API key

---

## Installation

### Step 1: Install Dependencies

```bash
cd rag-pipeline
pip install -r requirements-agent.txt
```

### Step 2: Configure API Keys

Add your OpenAI API key to `.env`:

```bash
echo "OPENAI_API_KEY=sk-your-openai-key-here" >> .env
```

Your `.env` should now contain:
```env
# From Spec 1
COHERE_API_KEY=your_cohere_key
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_key
QDRANT_COLLECTION_NAME=physical_ai_book

# New for Spec 3
OPENAI_API_KEY=sk-your-openai-key
```

### Step 3: Verify Setup

```bash
python check_setup.py
```

Expected output:
```
✓ Qdrant: Connected
✓ Collection: physical_ai_book (250 vectors)
```

---

## Usage

### Option 1: Interactive Chat (Recommended for First Use)

```bash
python rag_agent.py --interactive
```

Try these questions:
```
You: What is physical AI?
You: What are the main simulation tools?
You: Tell me more about Gazebo
You: exit
```

### Option 2: Single Query

```bash
python rag_agent.py --query "What is physical AI?"
```

### Option 3: Python API

Create a file `test_agent.py`:

```python
from rag_agent import RAGAgent

# Initialize
agent = RAGAgent()

# Ask a question
result = agent.query("What is physical AI?")
print(result['response'])

# Show sources
for source in result['sources'][:3]:
    print(f"- {source['title']} (Score: {source['score']:.3f})")
```

Run it:
```bash
python test_agent.py
```

---

## Running Tests

```bash
python test_rag_agent.py
```

Expected output:
```
[Test 1] Agent Initialization - ✓ PASSED
[Test 2] Single Query - ✓ PASSED
[Test 3] Context Retrieval - ✓ PASSED
[Test 4] Response Quality - ✓ PASSED
[Test 5] Multi-turn Conversation - ✓ PASSED
[Test 6] Module Filtering - ✓ PASSED

Pass Rate: 100%
```

---

## Common Commands

```bash
# Ask about a specific module
python rag_agent.py --query "Explain sensors" --module module-01

# Get more context (top-10 results)
python rag_agent.py --query "How does simulation work?" --top-k 10

# Interactive mode
python rag_agent.py --interactive

# Run tests
python test_rag_agent.py
```

---

## Troubleshooting

### Issue: "OPENAI_API_KEY is required"
**Solution:** Add `OPENAI_API_KEY` to your `.env` file

### Issue: "No results found"
**Solution:** Run `python ingest.py` to populate the Qdrant collection

### Issue: "Rate limit exceeded"
**Solution:** Wait a minute and try again, or upgrade your OpenAI API tier

---

## Next Steps

1. ✅ You've completed Spec 3!
2. Try asking more complex questions
3. Explore the Python API for custom integrations
4. See `SPEC3_IMPLEMENTATION_COMPLETE.md` for full documentation

---

## Support

- **Full Documentation:** `SPEC3_IMPLEMENTATION_COMPLETE.md`
- **API Reference:** See `rag_agent.py` docstrings
- **Test Examples:** See `test_rag_agent.py`

---

Happy building! 🚀
