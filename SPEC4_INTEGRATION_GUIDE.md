# Spec 4: Frontend-Backend Integration Guide

**Status:** ✅ Complete
**Date:** December 26, 2025

---

## Overview

This guide covers the complete integration of the RAG agent (Spec 3) with the Docusaurus frontend, enabling users to ask questions about Physical AI through a web interface.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER BROWSER                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Docusaurus Frontend (React + TypeScript)          │     │
│  │  - RAGChat Component                               │     │
│  │  - /ask-ai page                                    │     │
│  │  Port: 3000                                        │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           ↓ HTTP POST /api/query
                           ↓ (CORS enabled)
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND SERVER                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  FastAPI Server (Python)                           │     │
│  │  - POST /api/query                                 │     │
│  │  - GET /api/health                                 │     │
│  │  Port: 8000                                        │     │
│  └────────────────────────────────────────────────────┘     │
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │  RAG Agent (Spec 3)                                │     │
│  │  - OpenAI Agents SDK                               │     │
│  │  - Session memory                                  │     │
│  │  - Tracing support                                 │     │
│  └────────────────────────────────────────────────────┘     │
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Qdrant Vector Database                            │     │
│  │  - Collection: physical_ai_book                    │     │
│  │  - Cohere embeddings                               │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Backend API Server

**File:** `backend/api_server.py`

**Features:**
- FastAPI REST API server
- CORS enabled for local development
- Async agent execution
- Session support
- Health check endpoint
- Automatic API documentation

**Endpoints:**

| Method | Endpoint       | Description                  |
|--------|----------------|------------------------------|
| GET    | `/`            | API information              |
| GET    | `/api/health`  | Health check & agent status  |
| POST   | `/api/query`   | Send query to RAG agent      |
| GET    | `/docs`        | Interactive API docs (Swagger UI) |

**Request Format (POST /api/query):**
```json
{
  "query": "What is physical AI?",
  "session_id": "user123",
  "use_tracing": false
}
```

**Response Format:**
```json
{
  "query": "What is physical AI?",
  "response": "Physical AI refers to artificial intelligence systems...",
  "conversation_items": 2,
  "usage": {
    "requests": 1,
    "input_tokens": 150,
    "output_tokens": 200,
    "total_tokens": 350
  }
}
```

### 2. Frontend RAG Chat Component

**File:** `physical-ai-book/src/components/RAGChat/index.tsx`

**Features:**
- Interactive chat interface
- Real-time messaging
- Example questions
- Loading states
- Error handling
- Auto-scroll to latest message
- Session-based conversations

**Usage:**
```tsx
import RAGChat from '@site/src/components/RAGChat';

function MyPage() {
  return <RAGChat />;
}
```

### 3. Ask AI Page

**File:** `physical-ai-book/src/pages/ask-ai.tsx`

**Features:**
- Dedicated page for AI assistant
- Educational content about RAG system
- Technical stack information
- Full-width chat interface

**Access:** http://localhost:3000/ask-ai

---

## Installation & Setup

### Step 1: Install Backend Dependencies

```bash
# Navigate to backend directory
cd backend

# Install FastAPI and dependencies
pip install -r requirements.txt

# Install RAG agent dependencies (from Spec 3)
cd ../rag-pipeline
pip install -r requirements-agent.txt
cd ../backend
```

**Dependencies installed:**
- `fastapi>=0.115.0` - Web framework
- `uvicorn[standard]>=0.32.0` - ASGI server
- `python-dotenv>=1.0.0` - Environment variables
- Plus all RAG agent dependencies (OpenAI Agents SDK, Cohere, Qdrant, etc.)

### Step 2: Verify Environment Variables

Your `.env` file should already have these from Spec 3:

```env
# OpenAI
OPENAI_API_KEY=sk-proj-...

# Cohere (for embeddings)
COHERE_API_KEY=...

# Qdrant (vector database)
QDRANT_URL=https://...
QDRANT_API_KEY=...
QDRANT_COLLECTION_NAME=physical_ai_book
```

### Step 3: Start Backend Server

```bash
cd backend
python api_server.py
```

**Expected output:**
```
================================================================================
Physical AI RAG API Server
================================================================================
Starting server on http://localhost:8000
API documentation: http://localhost:8000/docs
Health check: http://localhost:8000/api/health
================================================================================
🚀 Initializing RAG Agent...
✓ RAG Agent initialized
  Model: gpt-4o
  Collection: physical_ai_book
✅ RAG Agent initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Test Backend API

In a new terminal:

```bash
cd backend
python test_api.py
```

This will run 4 tests:
1. Health check
2. Single query
3. Multiple queries with session
4. Invalid query validation

**Or test manually:**

```bash
# Health check
curl http://localhost:8000/api/health

# Send query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is physical AI?"}'
```

### Step 5: Start Frontend Development Server

In a new terminal:

```bash
cd physical-ai-book
npm start
```

**Expected output:**
```
[INFO] Starting the development server...
[SUCCESS] Docusaurus website is running at: http://localhost:3000/
```

### Step 6: Access the Chat Interface

Open your browser to:
- **Chat Page:** http://localhost:3000/ask-ai
- **API Docs:** http://localhost:8000/docs

---

## Testing End-to-End Flow

### Manual Testing

1. **Start both servers:**
   - Backend: `python backend/api_server.py`
   - Frontend: `npm start` (in physical-ai-book/)

2. **Navigate to chat page:**
   - Open http://localhost:3000/ask-ai

3. **Test query flow:**
   - Click an example question or type your own
   - Click "Send"
   - Observe loading state
   - Verify response appears

### Automated Backend Tests

```bash
cd backend
python test_api.py
```

**Tests covered:**
- ✅ Health check endpoint
- ✅ Single query processing
- ✅ Session-based conversations
- ✅ Input validation
- ✅ Error handling

### Expected Behavior

**Successful query:**
1. User types question in frontend
2. Frontend sends POST request to backend
3. Backend validates request
4. RAG agent retrieves context from Qdrant
5. Agent generates response using GPT-4o
6. Backend returns formatted response
7. Frontend displays answer with timestamp

**Error cases:**
- Backend offline → Error message with instruction
- Invalid query → Validation error
- Agent error → Error message in chat

---

## Configuration

### Backend Configuration

**File:** `backend/api_server.py`

```python
# Server settings
HOST = "0.0.0.0"
PORT = 8000

# CORS origins (add production URLs later)
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# RAG agent settings (inherited from Spec 3)
MODEL = "gpt-4o"
TEMPERATURE = 0.7
MAX_TOKENS = 2000
COLLECTION_NAME = "physical_ai_book"
```

### Frontend Configuration

**Environment variable (optional):**

Create `physical-ai-book/.env.local`:

```env
REACT_APP_API_URL=http://localhost:8000
```

Default: `http://localhost:8000`

---

## API Reference

### POST /api/query

**Description:** Send a query to the RAG agent

**Request Body:**
```typescript
{
  query: string;           // Required, 1-1000 characters
  session_id?: string;     // Optional, for conversation history
  use_tracing?: boolean;   // Optional, enable tracing
}
```

**Response:**
```typescript
{
  query: string;
  response: string;
  conversation_items: number;
  usage?: {
    requests: number;
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
  };
}
```

**Status Codes:**
- `200` - Success
- `422` - Validation error (invalid input)
- `500` - Server error (agent failure)
- `503` - Service unavailable (agent not initialized)

### GET /api/health

**Description:** Check server and agent status

**Response:**
```typescript
{
  status: "healthy" | "degraded";
  agent_ready: boolean;
  message: string;
}
```

---

## Development Workflow

### Running Both Servers

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

### Making Changes

**Backend changes:**
- Server auto-reloads on file changes (uvicorn reload=True)
- Test with: `curl` or `python test_api.py`

**Frontend changes:**
- React auto-reloads on file changes
- Check browser console for errors
- Test in browser: http://localhost:3000/ask-ai

### Debugging

**Backend:**
- Check server logs in terminal
- Visit http://localhost:8000/docs for interactive API testing
- Enable tracing: Set `use_tracing: true` in request

**Frontend:**
- Open browser DevTools (F12)
- Check Console tab for errors
- Check Network tab for API requests
- Verify CORS headers in Network tab

---

## Production Considerations

### Security

1. **API Key Protection:**
   - Never expose `.env` file
   - Use environment variables in production
   - Rotate keys regularly

2. **CORS Configuration:**
   - Update `ALLOWED_ORIGINS` in `api_server.py`
   - Add production frontend domain
   - Remove localhost origins

3. **Rate Limiting:**
   - Add rate limiting middleware (e.g., `slowapi`)
   - Protect against abuse
   - Monitor usage

### Performance

1. **Caching:**
   - Cache frequent queries
   - Use Redis for session storage
   - Cache Qdrant responses

2. **Scaling:**
   - Use multiple backend workers
   - Load balancer for horizontal scaling
   - Separate Qdrant instance

### Monitoring

1. **Logging:**
   - Structured logging (JSON format)
   - Log all queries and responses
   - Track error rates

2. **Metrics:**
   - Track response times
   - Monitor token usage
   - Alert on failures

---

## Troubleshooting

### Issue: Cannot connect to backend

**Symptoms:**
- Frontend shows connection error
- "Failed to fetch" in console

**Solutions:**
1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check backend logs for errors
3. Ensure port 8000 is not in use
4. Check firewall settings

### Issue: CORS errors

**Symptoms:**
- "CORS policy" errors in console
- Requests blocked by browser

**Solutions:**
1. Verify frontend origin in `ALLOWED_ORIGINS`
2. Check CORS headers in Network tab
3. Restart backend server after changes

### Issue: Agent not responding

**Symptoms:**
- 503 Service Unavailable
- "Agent not initialized" message

**Solutions:**
1. Check `.env` file has all required keys
2. Verify Qdrant connection
3. Check OpenAI API key is valid
4. Review backend startup logs

### Issue: Slow responses

**Symptoms:**
- Long wait times (>10 seconds)
- Timeouts

**Solutions:**
1. Check Qdrant connection speed
2. Reduce `top_k` in retrieval
3. Use smaller `max_tokens`
4. Check OpenAI API status

---

## File Structure

```
physical-ai-hackathon/
├── backend/
│   ├── api_server.py           # FastAPI server
│   ├── requirements.txt        # Backend dependencies
│   └── test_api.py             # API tests
│
├── rag-pipeline/
│   ├── rag_agent.py            # RAG agent (Spec 3)
│   └── requirements-agent.txt  # Agent dependencies
│
├── physical-ai-book/
│   └── src/
│       ├── components/
│       │   └── RAGChat/
│       │       ├── index.tsx   # Chat component
│       │       └── styles.module.css
│       └── pages/
│           └── ask-ai.tsx      # Chat page
│
└── .env                        # Environment variables
```

---

## Next Steps

### Immediate (Post-Testing)
1. ✅ Verify all endpoints work
2. ✅ Test multiple queries
3. ✅ Check session persistence
4. ✅ Validate error handling

### Short-term (Enhancement)
1. Add user authentication
2. Store conversation history
3. Add query suggestions
4. Implement feedback system

### Long-term (Production)
1. Deploy backend to cloud (AWS/GCP/Azure)
2. Configure production CORS
3. Add monitoring and logging
4. Implement caching layer
5. Add rate limiting
6. Performance optimization

---

## Success Criteria

✅ **All criteria met:**

1. ✅ Frontend can send user queries to the Agent
   - RAGChat component sends POST requests
   - Request includes query, session_id, tracing flag

2. ✅ Agent returns relevant responses to frontend
   - Backend processes queries via RAG agent
   - Responses include answer, metadata, usage stats

3. ✅ End-to-end pipeline works locally
   - Backend runs on port 8000
   - Frontend runs on port 3000
   - CORS configured for local development
   - All tests pass

---

## Technical Stack Summary

| Layer          | Technology                    | Purpose                        |
|----------------|-------------------------------|--------------------------------|
| Frontend       | React + TypeScript            | User interface                 |
| Frontend Framework | Docusaurus 3.9.2         | Documentation site generator   |
| Backend        | FastAPI + Python              | REST API server                |
| AI Agent       | OpenAI Agents SDK             | Agentic workflow               |
| LLM            | GPT-4o                        | Response generation            |
| Vector DB      | Qdrant                        | Semantic search                |
| Embeddings     | Cohere embed-english-v3.0     | Query vectorization            |
| Session        | SQLiteSession                 | Conversation history           |

---

## Resources

- **Backend API Docs:** http://localhost:8000/docs
- **Frontend Chat:** http://localhost:3000/ask-ai
- **Health Check:** http://localhost:8000/api/health

---

**Status:** ✅ Integration Complete
**Date:** December 26, 2025
**Implementation:** Spec 4 - Frontend-Backend Integration
**Dependencies:** Spec 3 (RAG Agent), Spec 1 (Vector Database)
