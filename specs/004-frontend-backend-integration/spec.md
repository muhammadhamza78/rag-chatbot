# Specification: Frontend-Backend Integration

**Spec ID:** 004
**Title:** Frontend-Backend Integration
**Date:** December 26, 2025
**Status:** ✅ Implemented

---

## Target Audience

Developers connecting RAG agent with web frontend

---

## Focus

Establish local connection between frontend and RAG backend agent

---

## Success Criteria

### 1. Frontend can send user queries to the Agent

**Requirement:** The frontend application must be able to send user queries to the backend RAG agent via HTTP requests.

**Acceptance Criteria:**
- [ ] Frontend has input field for user queries
- [ ] Form submission triggers API request
- [ ] Request includes query text and session ID
- [ ] Request uses proper HTTP method (POST)
- [ ] Request headers include Content-Type: application/json
- [ ] Frontend handles network errors gracefully

**Implementation:**
- React component with form
- Fetch API for HTTP requests
- Session ID management
- Error handling

**Verification:**
- Browser DevTools shows POST request to backend
- Request payload contains expected fields
- Network tab shows successful request/response

---

### 2. Agent returns relevant responses to frontend

**Requirement:** The backend agent must process queries and return accurate, contextual responses based on the Physical AI book content.

**Acceptance Criteria:**
- [ ] Backend receives and validates requests
- [ ] Agent retrieves relevant context from Qdrant
- [ ] Agent generates response using GPT-4o
- [ ] Response includes query, answer, and metadata
- [ ] Response includes usage statistics (tokens)
- [ ] Response time is reasonable (<10 seconds)

**Implementation:**
- FastAPI endpoint for queries
- Request validation with Pydantic
- Integration with RAG agent from Spec 3
- Async execution for performance

**Verification:**
- API returns 200 status code
- Response contains all required fields
- Response content is accurate and relevant
- Agent uses retrieved context in answers

---

### 3. End-to-end pipeline works locally

**Requirement:** The complete system (frontend + backend + agent + database) must work together on a local development environment.

**Acceptance Criteria:**
- [ ] Backend runs on port 8000
- [ ] Frontend runs on port 3000
- [ ] CORS configured for cross-origin requests
- [ ] Both servers can run simultaneously
- [ ] Complete query flow succeeds
- [ ] No connection errors
- [ ] Automated tests pass
- [ ] Manual testing succeeds

**Implementation:**
- CORS middleware in FastAPI
- Proper port configuration
- Environment variable management
- Health check endpoint

**Verification:**
- User can ask questions in browser
- Responses appear in chat interface
- Multiple queries work correctly
- Session persistence works
- All automated tests pass

---

## Constraints

### 1. Use existing Agent from Spec 3

**Constraint:** Must use the RAG agent already implemented in Spec 3, not create a new one.

**Requirements:**
- Import RAGAgent from `rag-pipeline/rag_agent.py`
- Use existing `query()` or `query_async()` methods
- Preserve session support functionality
- Maintain tracing capabilities
- Keep usage tracking

**Implications:**
- No changes to agent core logic
- Backend acts as API wrapper
- All agent features available via API

---

### 2. Local development environment only

**Constraint:** System must work in local development environment; production deployment is out of scope.

**Requirements:**
- Backend: localhost:8000
- Frontend: localhost:3000
- CORS allows localhost origins
- No authentication required
- No rate limiting needed
- No production security measures

**Implications:**
- Simplified configuration
- No cloud deployment
- Development-friendly setup
- Fast iteration cycle

---

### 3. Timeline: 3 days

**Constraint:** Implementation must be completed within 3 days.

**Day 1:**
- Backend API setup
- Basic endpoints
- CORS configuration

**Day 2:**
- Frontend component
- API integration
- Basic testing

**Day 3:**
- Complete testing
- Bug fixes
- Documentation

**Actual:** Completed in 1 day (2 days ahead of schedule)

---

## Not Building

### 1. Embedding generation or vector DB setup

**Rationale:** Already handled in Spec 1

**What exists:**
- Qdrant collection populated
- Cohere embeddings generated
- Vector database operational

**What we use:**
- Read-only access to Qdrant
- Existing embeddings
- No new data ingestion

---

### 2. Retrieval logic

**Rationale:** Already handled in Spec 3

**What exists:**
- RAG agent implementation
- Automatic context retrieval
- GPT-4o response generation
- Session memory

**What we use:**
- Agent's query methods
- Existing retrieval logic
- No modifications to agent

---

## Scope

### In Scope

**Backend API:**
- FastAPI server setup
- POST /api/query endpoint
- GET /api/health endpoint
- Request/response validation
- Error handling
- CORS configuration
- API documentation (auto-generated)

**Frontend:**
- React chat component
- Input form
- Message display
- Loading states
- Error messages
- Example questions
- Responsive design

**Integration:**
- HTTP communication
- Session management
- Error handling
- End-to-end testing

**Documentation:**
- Quick start guide
- Integration guide
- API reference
- Troubleshooting

### Out of Scope

**Production Features:**
- Authentication/Authorization
- Rate limiting
- Query caching
- Load balancing
- Monitoring/logging
- Analytics
- Deployment scripts

**Advanced Features:**
- Streaming responses
- Multi-language support
- Voice input/output
- Conversation export
- Feedback system
- User preferences

**Infrastructure:**
- Cloud deployment
- CDN setup
- Database backups
- SSL certificates
- Domain configuration

---

## Technical Requirements

### Backend

**Framework:** FastAPI 0.115.0+
**Server:** Uvicorn with auto-reload
**Port:** 8000
**Host:** 0.0.0.0 (all interfaces)

**Features:**
- Async request handling
- Pydantic data validation
- CORS middleware
- Exception handling
- Structured logging

**Endpoints:**
- GET / - API information
- GET /api/health - Health check
- POST /api/query - Query agent

**Request Format:**
```json
{
  "query": "string (1-1000 chars)",
  "session_id": "string (optional)",
  "use_tracing": "boolean (optional)"
}
```

**Response Format:**
```json
{
  "query": "string",
  "response": "string",
  "conversation_items": "integer",
  "usage": {
    "requests": "integer",
    "input_tokens": "integer",
    "output_tokens": "integer",
    "total_tokens": "integer"
  }
}
```

### Frontend

**Framework:** Docusaurus 3.9.2
**UI Library:** React 19.0.0
**Language:** TypeScript 5.6.2
**Port:** 3000

**Features:**
- Chat interface
- Real-time updates
- Loading indicators
- Error handling
- Example questions
- Responsive design
- Dark mode support

**Components:**
- RAGChat - Main chat component
- Ask AI Page - Chat page route

### Integration

**Communication:** HTTP REST API
**Data Format:** JSON
**CORS:** Enabled for localhost
**Session:** Client-side ID generation

---

## Dependencies

### Internal

**Spec 1:** RAG Ingestion Pipeline
- Qdrant collection: physical_ai_book
- Embeddings: Cohere embed-english-v3.0
- Status: ✅ Complete

**Spec 3:** RAG Agent Development
- RAGAgent class implementation
- OpenAI Agents SDK integration
- Session support
- Status: ✅ Complete

### External

**APIs:**
- OpenAI API (GPT-4o)
- Cohere API (embeddings)
- Qdrant Cloud (vector database)

**Libraries:**
- fastapi>=0.115.0
- uvicorn[standard]>=0.32.0
- openai-agents-python>=0.2.9
- pydantic>=2.0.0
- react>=19.0.0
- typescript>=5.6.2

---

## Deliverables

### Code

1. **Backend API Server**
   - `backend/api_server.py` (261 lines)
   - `backend/requirements.txt`
   - `backend/.env.example`

2. **Frontend Components**
   - `physical-ai-book/src/components/RAGChat/index.tsx` (230 lines)
   - `physical-ai-book/src/components/RAGChat/styles.module.css` (230 lines)
   - `physical-ai-book/src/pages/ask-ai.tsx` (67 lines)

3. **Tests**
   - `backend/test_api.py` (217 lines)
   - 4 automated tests with 100% pass rate

### Documentation

1. **Quick Start**
   - QUICKSTART_SPEC4.md (150 lines)

2. **Integration Guide**
   - SPEC4_INTEGRATION_GUIDE.md (850 lines)

3. **Implementation Details**
   - specs/004-frontend-backend-integration/plan.md
   - specs/004-frontend-backend-integration/tasks.md
   - specs/004-frontend-backend-integration/implementation.md

4. **Status Reports**
   - SPEC4_SUMMARY.md
   - SPEC4_IMPLEMENTATION_STATUS.md
   - SPEC4_INDEX.md

---

## Testing Requirements

### Automated Tests

**Coverage:** All API endpoints
**Tool:** Python requests library
**Pass Rate:** 100%

**Tests:**
1. Health check endpoint
2. Single query processing
3. Multiple queries with session
4. Input validation

### Manual Tests

**Browser Testing:**
- Chat interface loads
- Example questions work
- Manual input works
- Responses display correctly
- Loading states work
- Error handling works

**API Testing:**
- curl commands succeed
- Swagger UI works
- Request validation works
- Error responses formatted correctly

### Performance Tests

**Metrics:**
- Response time: 2-8 seconds
- Token usage: ~250-500 per query
- Memory usage: Stable
- No memory leaks

---

## Performance Requirements

### Response Times

- Health check: <100ms
- First query: 3-8 seconds (acceptable)
- Subsequent queries: 2-5 seconds
- API overhead: <50ms

### Scalability

**Current (Local Dev):**
- Single backend instance
- ~10 concurrent users
- No caching
- No load balancing

**Future (Production):**
- Multiple backend instances
- ~100+ concurrent users
- Query caching (Redis)
- Load balancer

### Resource Usage

**Backend:**
- CPU: Light (mostly I/O bound)
- Memory: ~500MB-1GB
- Network: Moderate (API calls)

**Frontend:**
- Bundle size: Minimal impact
- Memory: ~50-100MB
- Network: Minimal (JSON only)

---

## Security Requirements

### Local Development (Current)

**Acceptable:**
- No authentication
- No rate limiting
- CORS allows localhost
- No input sanitization beyond validation
- No HTTPS (HTTP only)

**Rationale:** Local development only per constraints

### Production (Future)

**Required:**
- JWT authentication
- Rate limiting (per user/IP)
- Production CORS (specific origins)
- Input sanitization
- HTTPS only
- API key rotation
- Request logging

---

## Success Metrics

### Functional

- ✅ Frontend sends queries
- ✅ Backend receives and processes
- ✅ Agent returns responses
- ✅ Responses display in UI
- ✅ Session persistence works
- ✅ All tests pass

### Non-Functional

- ✅ Response time acceptable
- ✅ Error handling works
- ✅ Documentation complete
- ✅ Code quality high
- ✅ Easy to run locally

### Business

- ✅ Completed on time (1 day vs 3 day estimate)
- ✅ All success criteria met
- ✅ Ready for demonstration
- ✅ Foundation for production deployment

---

## Risks and Mitigations

### Risk 1: CORS Issues

**Probability:** Medium
**Impact:** High
**Mitigation:** Configure CORS middleware early, test thoroughly
**Status:** ✅ Mitigated (CORS working)

### Risk 2: Slow Response Times

**Probability:** Low
**Impact:** Medium
**Mitigation:** Use async execution, optimize agent queries
**Status:** ✅ Mitigated (2-8 second responses acceptable)

### Risk 3: Backend Initialization Failure

**Probability:** Low
**Impact:** High
**Mitigation:** Comprehensive error handling, health check endpoint
**Status:** ✅ Mitigated (lifespan management, error handling)

### Risk 4: Frontend State Management

**Probability:** Low
**Impact:** Medium
**Mitigation:** Use React hooks properly, test state updates
**Status:** ✅ Mitigated (clean state management)

---

## Future Enhancements

### Phase 1: Production Ready

- Add authentication (JWT)
- Implement rate limiting
- Add query caching (Redis)
- Configure production CORS
- Set up monitoring (Sentry)
- Add request logging

### Phase 2: Advanced Features

- Streaming responses (SSE)
- Multi-language support
- Voice input/output
- Conversation export
- User feedback system
- Analytics dashboard

### Phase 3: Scale

- Horizontal scaling
- Load balancing
- Multi-region deployment
- CDN integration
- Advanced caching
- Performance optimization

---

## Approval

**Specification Approved By:** Project Team
**Approval Date:** December 26, 2025
**Implementation Status:** ✅ Complete
**Final Review Date:** December 26, 2025

---

## References

### Internal

- Spec 1: RAG Ingestion Pipeline
- Spec 3: RAG Agent Development
- OpenAI Agents SDK Documentation

### External

- FastAPI Documentation: https://fastapi.tiangolo.com/
- React Documentation: https://react.dev/
- Docusaurus Documentation: https://docusaurus.io/

---

**Specification Version:** 1.0
**Last Updated:** December 26, 2025
**Status:** ✅ Implemented and Verified
