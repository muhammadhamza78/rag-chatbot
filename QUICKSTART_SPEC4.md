# Quick Start: Frontend-Backend Integration (Spec 4)

Get the full RAG chat system running in 5 minutes.

## Prerequisites

- ✅ Spec 3 completed (RAG agent)
- ✅ Python 3.8+
- ✅ Node.js 20+
- ✅ Environment variables configured

## Installation

### 1. Install Backend Dependencies (1 minute)

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# RAG agent dependencies (if not installed)
cd ../rag-pipeline
pip install -r requirements-agent.txt
```

### 2. Install Frontend Dependencies (if needed)

```bash
cd physical-ai-book
npm install
```

## Running the System

### Terminal 1: Start Backend (30 seconds)

```bash
cd backend
python api_server.py
```

**Wait for:**
```
✅ RAG Agent initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Start Frontend (30 seconds)

```bash
cd physical-ai-book
npm start
```

**Wait for:**
```
[SUCCESS] Docusaurus website is running at: http://localhost:3000/
```

## Testing

### Quick Test (30 seconds)

**Option 1: Browser**
1. Open http://localhost:3000/ask-ai
2. Click "What is physical AI?"
3. Verify response appears

**Option 2: API Test**
```bash
cd backend
python test_api.py
```

**Option 3: Manual curl**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is physical AI?"}'
```

## URLs

- 🌐 **Chat Interface:** http://localhost:3000/ask-ai
- 📚 **API Docs:** http://localhost:8000/docs
- ✅ **Health Check:** http://localhost:8000/api/health

## Troubleshooting

### Backend won't start
```bash
# Check environment variables
cat ../.env | grep -E "(OPENAI|COHERE|QDRANT)"

# Verify Qdrant connection
python -c "from qdrant_client import QdrantClient; print('OK')"
```

### Frontend can't connect
1. Ensure backend shows: `✅ RAG Agent initialized successfully`
2. Check http://localhost:8000/api/health returns `"agent_ready": true`
3. Verify no CORS errors in browser console (F12)

### Slow responses
- Normal: 3-8 seconds for first query
- Subsequent queries: 2-5 seconds
- Check OpenAI API status if slower

## What You Get

✅ **Full RAG System:**
- Interactive chat interface
- Intelligent context retrieval
- GPT-4o powered responses
- Session-based conversations
- Real-time token usage tracking

✅ **Development Tools:**
- Auto-reload on code changes
- Interactive API docs
- Automated tests
- Error handling

## Next Steps

1. **Explore:** Try different questions at http://localhost:3000/ask-ai
2. **API:** Check out http://localhost:8000/docs
3. **Customize:** Edit `backend/api_server.py` or `physical-ai-book/src/components/RAGChat/`
4. **Deploy:** See `SPEC4_INTEGRATION_GUIDE.md` for production deployment

## File Locations

```
physical-ai-hackathon/
├── backend/
│   ├── api_server.py       ← Backend server
│   └── test_api.py         ← Tests
│
└── physical-ai-book/
    └── src/
        ├── components/RAGChat/  ← Chat component
        └── pages/ask-ai.tsx     ← Chat page
```

## Support

- **Full Guide:** `SPEC4_INTEGRATION_GUIDE.md`
- **Backend README:** `backend/README.md`
- **API Docs:** http://localhost:8000/docs

---

**Status:** Ready to use
**Time to setup:** ~5 minutes
**Dependencies:** Spec 1 (embeddings) + Spec 3 (agent)
