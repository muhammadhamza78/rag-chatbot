# Backend API Server

FastAPI backend for Physical AI RAG Agent (Spec 4)

## Quick Start

### 1. Install Dependencies

```bash
# Install backend dependencies
pip install -r requirements.txt

# Install RAG agent dependencies
cd ../rag-pipeline
pip install -r requirements-agent.txt
cd ../backend
```

### 2. Configure Environment

Ensure `.env` file exists in project root with:

```env
OPENAI_API_KEY=sk-proj-...
COHERE_API_KEY=...
QDRANT_URL=https://...
QDRANT_API_KEY=...
QDRANT_COLLECTION_NAME=physical_ai_book
```

### 3. Start Server

```bash
python api_server.py
```

Server starts on: http://localhost:8000

### 4. Test API

```bash
# Run automated tests
python test_api.py

# Or test manually
curl http://localhost:8000/api/health
```

## API Endpoints

### GET /api/health
Check server and agent status

**Response:**
```json
{
  "status": "healthy",
  "agent_ready": true,
  "message": "RAG Agent ready"
}
```

### POST /api/query
Query the RAG agent

**Request:**
```json
{
  "query": "What is physical AI?",
  "session_id": "user123",
  "use_tracing": false
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

### GET /docs
Interactive API documentation (Swagger UI)

## Development

**Auto-reload enabled** - Server reloads on file changes

**CORS enabled** for:
- http://localhost:3000
- http://127.0.0.1:3000

## Files

- `api_server.py` - FastAPI application
- `test_api.py` - Automated API tests
- `requirements.txt` - Python dependencies

## Testing

```bash
# Run all tests
python test_api.py

# Manual tests
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ROS?"}'
```

## Architecture

```
Client Request
    ↓
FastAPI Server (api_server.py)
    ↓
RAG Agent (rag_agent.py)
    ↓
Qdrant Vector Database
    ↓
OpenAI GPT-4o
    ↓
Response
```

## Port Configuration

- **Backend:** 8000
- **Frontend:** 3000 (Docusaurus)

## Documentation

See `SPEC4_INTEGRATION_GUIDE.md` for complete integration guide.
