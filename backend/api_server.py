#!/usr/bin/env python3
"""
FastAPI Backend Server for RAG Agent
Spec 4: Frontend-Backend Integration

This server exposes the RAG agent from Spec 3 via REST API endpoints
for consumption by the Docusaurus frontend.

Features:
- POST /api/query - Send queries to RAG agent
- GET /api/health - Health check endpoint
- CORS enabled for local frontend development
- Session support for conversation history
- Async execution for better performance
"""

import sys
import os
from typing import Optional
from contextlib import asynccontextmanager

# Add rag-pipeline to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rag-pipeline'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

# Import RAG Agent
from rag_agent import RAGAgent

# Load environment variables
load_dotenv()

# Global agent instance
agent: Optional[RAGAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    Initializes RAG agent on startup and cleans up on shutdown.
    """
    global agent

    # Startup: Initialize RAG agent
    print("🚀 Initializing RAG Agent...")
    try:
        agent = RAGAgent()
        print("✅ RAG Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize RAG Agent: {e}")
        raise

    yield

    # Shutdown: Cleanup
    print("👋 Shutting down API server...")


# Create FastAPI app
app = FastAPI(
    title="Physical AI RAG API",
    description="Backend API for Physical AI educational book RAG agent",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Docusaurus dev server
        "http://127.0.0.1:3000",
        "http://localhost:8000",  # Alternative port
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class QueryRequest(BaseModel):
    """Request model for /api/query endpoint"""
    query: str = Field(..., min_length=1, max_length=1000, description="User question about Physical AI")
    session_id: Optional[str] = Field(None, description="Session ID for conversation history")
    use_tracing: bool = Field(False, description="Enable tracing for debugging")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is physical AI?",
                "session_id": "user123",
                "use_tracing": False
            }
        }


class QueryResponse(BaseModel):
    """Response model for /api/query endpoint"""
    query: str
    response: str
    conversation_items: int
    usage: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class HealthResponse(BaseModel):
    """Response model for /api/health endpoint"""
    status: str
    agent_ready: bool
    message: str


# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Physical AI RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        HealthResponse with status and agent readiness
    """
    agent_ready = agent is not None

    return HealthResponse(
        status="healthy" if agent_ready else "degraded",
        agent_ready=agent_ready,
        message="RAG Agent ready" if agent_ready else "RAG Agent not initialized"
    )


@app.post("/api/query", response_model=QueryResponse, tags=["Query"])
async def query_agent(request: QueryRequest):
    """
    Query the RAG agent with a user question.

    The agent will:
    1. Automatically retrieve relevant context from the Physical AI book
    2. Generate an accurate response based on retrieved content
    3. Include source citations in the response

    Args:
        request: QueryRequest with user query and optional session_id

    Returns:
        QueryResponse with agent's answer and metadata

    Raises:
        HTTPException: If agent not initialized or query fails
    """
    if agent is None:
        raise HTTPException(
            status_code=503,
            detail="RAG Agent not initialized. Check server logs."
        )

    try:
        # Query agent asynchronously
        result = await agent.query_async(
            user_query=request.query,
            session_id=request.session_id,
            use_tracing=request.use_tracing
        )

        return QueryResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


# Development server configuration
if __name__ == "__main__":
    print("=" * 80)
    print("Physical AI RAG API Server")
    print("=" * 80)
    print("Starting server on http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print("Health check: http://localhost:8000/api/health")
    print("=" * 80)

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
