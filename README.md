# Physical AI Hackathon - RAG System

Complete Retrieval-Augmented Generation (RAG) system for the Physical AI educational book with web interface.

**Status:** ✅ All specs complete and operational

---

## What is This?

An intelligent AI assistant that answers questions about Physical AI by:
1. Searching through the entire Physical AI book using vector similarity
2. Retrieving the most relevant content
3. Generating accurate, contextual answers using GPT-4o

**Try it:** http://localhost:3000/ask-ai (after starting servers)

---

## Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt
pip install -r ../rag-pipeline/requirements-agent.txt

# Frontend (if needed)
cd ../physical-ai-book
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```env
OPENAI_API_KEY=sk-proj-...
COHERE_API_KEY=...
QDRANT_URL=https://...
QDRANT_API_KEY=...
```

### 3. Start Servers

**Terminal 1 - Backend:**
```bash
cd backend
python api_server.py
```

**Terminal 2 - Frontend:**
```bash
cd physical-ai-book
npm start
```

### 4. Use Chat Interface

Open http://localhost:3000/ask-ai and ask a question!

---

## Features

### AI Assistant
- ✅ Intelligent question answering
- ✅ Context-aware responses
- ✅ Source citations from the book
- ✅ Multi-turn conversations
- ✅ Session memory

### Backend API
- ✅ REST API with FastAPI
- ✅ Automatic API documentation
- ✅ Health monitoring
- ✅ CORS enabled
- ✅ Async execution

### Frontend Interface
- ✅ Interactive chat UI
- ✅ Example questions
- ✅ Real-time responses
- ✅ Loading states
- ✅ Error handling
- ✅ Responsive design

### Technical
- ✅ OpenAI Agents SDK
- ✅ GPT-4o for generation
- ✅ Qdrant vector database
- ✅ Cohere embeddings
- ✅ Session persistence
- ✅ Usage tracking

---

## Architecture

```
Frontend (React)  →  Backend (FastAPI)  →  RAG Agent  →  Qdrant
    Port 3000            Port 8000          GPT-4o       Vector DB
```

**Flow:**
1. User asks question in browser
2. Frontend sends to backend API
3. Backend queries RAG agent
4. Agent retrieves context from Qdrant
5. GPT-4o generates answer
6. Response displayed in chat

---

## Project Structure

```
physical-ai-hackathon/
├── backend/                 # FastAPI REST API
│   ├── api_server.py       # Main server
│   ├── test_api.py         # API tests
│   └── requirements.txt
│
├── rag-pipeline/            # RAG agent & data
│   ├── rag_agent.py        # OpenAI Agents SDK
│   ├── config.py           # Configuration
│   └── requirements-agent.txt
│
├── physical-ai-book/        # Docusaurus frontend
│   └── src/
│       ├── components/RAGChat/  # Chat component
│       └── pages/ask-ai.tsx     # Chat page
│
└── docs/                    # Documentation
    ├── QUICKSTART_SPEC4.md
    ├── SPEC4_INTEGRATION_GUIDE.md
    └── PROJECT_STATUS.md
```

---

## Documentation

### Quick References

- **[QUICKSTART_SPEC4.md](QUICKSTART_SPEC4.md)** - 5-minute setup
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Complete project overview
- **[backend/README.md](backend/README.md)** - Backend API reference

### Complete Guides

- **[SPEC4_INTEGRATION_GUIDE.md](SPEC4_INTEGRATION_GUIDE.md)** - Full integration guide
- **[SPEC4_INDEX.md](SPEC4_INDEX.md)** - Documentation navigation
- **[AGENTS_SDK_MIGRATION.md](rag-pipeline/AGENTS_SDK_MIGRATION.md)** - Agent SDK details

---

## API Reference

### POST /api/query
Send a question to the AI assistant

**Request:**
```json
{
  "query": "What is physical AI?",
  "session_id": "user123"
}
```

**Response:**
```json
{
  "query": "What is physical AI?",
  "response": "Physical AI refers to...",
  "conversation_items": 2,
  "usage": {
    "total_tokens": 350
  }
}
```

### GET /api/health
Check system status

**Interactive docs:** http://localhost:8000/docs

---

## Testing

### Automated Tests

```bash
cd backend
python test_api.py
```

**Output:**
```
Tests Passed: 4/4
Success Rate: 100.0%
✅ All tests passed!
```

### Manual Testing

**Browser:**
- Visit http://localhost:3000/ask-ai
- Ask: "What is physical AI?"
- Verify response

**curl:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ROS?"}'
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | React + TypeScript (Docusaurus 3.9.2) |
| Backend | FastAPI + Python |
| AI Agent | OpenAI Agents SDK |
| LLM | GPT-4o |
| Vector DB | Qdrant |
| Embeddings | Cohere embed-english-v3.0 |

---

## Requirements

- Python 3.8+
- Node.js 20+
- OpenAI API key
- Cohere API key
- Qdrant instance

---

## Development

### Backend Development

```bash
cd backend
python api_server.py  # Auto-reloads on changes
```

**API docs:** http://localhost:8000/docs

### Frontend Development

```bash
cd physical-ai-book
npm start  # Auto-reloads on changes
```

**Chat page:** http://localhost:3000/ask-ai

---

## Troubleshooting

### Backend won't start
- Check `.env` file exists with all keys
- Verify Qdrant connection: `curl $QDRANT_URL`
- Check OpenAI API key is valid

### Frontend can't connect
- Ensure backend is running: `curl http://localhost:8000/api/health`
- Check for CORS errors in browser console (F12)
- Verify backend shows "✅ RAG Agent initialized successfully"

### Slow responses
- First query: 3-8 seconds (normal cold start)
- Subsequent: 2-5 seconds
- Check OpenAI API status if slower

**Full troubleshooting:** [SPEC4_INTEGRATION_GUIDE.md](SPEC4_INTEGRATION_GUIDE.md) → Troubleshooting

---

## Key URLs

| Service | URL |
|---------|-----|
| Chat Interface | http://localhost:3000/ask-ai |
| API Documentation | http://localhost:8000/docs |
| Health Check | http://localhost:8000/api/health |
| Frontend | http://localhost:3000 |

---

## Specs Overview

### Spec 1: RAG Ingestion Pipeline ✅
- Crawled Physical AI book
- Generated embeddings
- Stored in Qdrant

### Spec 2: Retrieval Testing ✅
- Validated vector search
- Tested retrieval accuracy
- Benchmarked performance

### Spec 3: RAG Agent Development ✅
- Built agent with OpenAI Agents SDK
- Automatic context retrieval
- GPT-4o response generation
- Session memory & tracing

### Spec 4: Frontend-Backend Integration ✅
- FastAPI REST API
- React chat interface
- End-to-end working system
- Complete documentation

---

## Performance

- **Response time:** 2-8 seconds
- **Token usage:** ~250-500 per query
- **Cost:** ~$0.001-0.003 per query
- **Accuracy:** High (uses actual book content)

---

## Known Limitations

**Current (acceptable for local dev):**
- No authentication
- No rate limiting
- No query caching
- Single backend instance

**These are intentional** - Spec 4 is for local development only.

---

## Future Enhancements

- [ ] User authentication
- [ ] Rate limiting
- [ ] Query caching (Redis)
- [ ] Streaming responses
- [ ] Multi-language support
- [ ] Production deployment

---

## Contributing

This is a hackathon project. For production use:
1. Add authentication
2. Implement rate limiting
3. Set up monitoring
4. Deploy to cloud
5. Configure production CORS

---

## License

- **Code:** MIT
- **Content:** CC BY-SA 4.0

---

## Support

- **Documentation:** See `SPEC4_INDEX.md`
- **Quick Start:** See `QUICKSTART_SPEC4.md`
- **Full Guide:** See `SPEC4_INTEGRATION_GUIDE.md`
- **Status:** See `PROJECT_STATUS.md`

---

## Quick Commands

```bash
# Start everything
cd backend && python api_server.py &
cd physical-ai-book && npm start

# Run tests
cd backend && python test_api.py

# Check health
curl http://localhost:8000/api/health

# Query API
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is physical AI?"}'
```

---

**Status:** ✅ Complete and operational
**Last Updated:** December 26, 2025

🎉 **Ready to use! Visit http://localhost:3000/ask-ai after starting servers.**
