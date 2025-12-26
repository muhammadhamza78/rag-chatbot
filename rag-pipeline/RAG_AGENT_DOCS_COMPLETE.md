# RAG Agent for Physical AI Book

**Spec 3 Implementation: RAG Agent Development**

An intelligent agent that combines OpenAI's Agents SDK with Qdrant vector retrieval to provide accurate, context-aware responses about Physical AI topics.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Examples](#examples)
7. [Python API](#python-api)
8. [Testing](#testing)
9. [Architecture](#architecture-details)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This RAG (Retrieval-Augmented Generation) Agent:
1. **Accepts user queries** about Physical AI, robotics, simulation, and related topics
2. **Retrieves relevant context** from the Qdrant vector database (populated by Spec 1)
3. **Generates accurate responses** using OpenAI's GPT models with retrieved context
4. **Supports multi-turn conversations** with context awareness

### Architecture Diagram

```
User Query
    ↓
Query Embedding (Cohere)
    ↓
Vector Search (Qdrant) → Retrieved Chunks
    ↓
Context Formatting
    ↓
OpenAI Assistant (GPT-4) → Response
    ↓
User
```

---

## Features

- ✅ **OpenAI Agents SDK Integration**: Uses the official OpenAI Assistants API
- ✅ **Vector Retrieval**: Queries Qdrant for relevant content from the Physical AI book
- ✅ **Context-Aware Responses**: Combines retrieved context with LLM generation
- ✅ **Multi-Turn Conversations**: Maintains conversation history via threads
- ✅ **Module Filtering**: Optional filtering by book module (module-01, module-02, etc.)
- ✅ **Source Citations**: Returns source documents with relevance scores
- ✅ **Interactive & Programmatic**: CLI interface + Python API

---

## Prerequisites

1. **Completed Spec 1**: Vector database must be populated with embeddings
2. **API Keys**:
   - OpenAI API key (GPT-4 access recommended)
   - Cohere API key (for query embeddings)
   - Qdrant Cloud credentials (URL + API key)

---

## Installation

### 1. Install Dependencies

```bash
cd rag-pipeline
pip install -r requirements-agent.txt
```

### 2. Configure Environment

Add to your `.env` file:

```env
# Existing Qdrant & Cohere config (from Spec 1)
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=physical_ai_book
COHERE_API_KEY=your_cohere_api_key

# New: OpenAI API Key
OPENAI_API_KEY=your_openai_api_key
```

### 3. Verify Setup

Ensure your Qdrant collection is populated:

```bash
python check_setup.py
```

You should see confirmation that the collection exists with vectors.

---

## Usage

### Quick Start

```bash
# Ask a single question
python rag_agent.py --query "What is physical AI?"

# Interactive chat mode
python rag_agent.py --interactive

# Filter by module
python rag_agent.py --query "Explain sensors" --module module-01

# Get more context
python rag_agent.py --query "How does Gazebo work?" --top-k 10
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--query TEXT` | Ask a single question | None |
| `--interactive` | Enter interactive chat mode | False |
| `--top-k N` | Number of context chunks to retrieve | 5 |
| `--module MODULE` | Filter by module (e.g., module-01) | None |

---

## Examples

### Example 1: Single Query

```bash
python rag_agent.py --query "What is physical AI?"
```

**Output:**
```
Initializing RAG Agent...
✓ RAG Agent initialized
  Model: gpt-4-turbo-preview
  Collection: physical_ai_book

🔍 Retrieving context for: 'What is physical AI?'
✓ Retrieved 5 relevant chunks
🤖 Generating response...
✓ Response generated

================================================================================
QUERY: What is physical AI?
================================================================================

RESPONSE:
Physical AI refers to artificial intelligence systems that interact with and
manipulate the physical world. Unlike traditional AI that operates purely in
digital spaces, physical AI combines intelligent algorithms with robotic
systems, sensors, and actuators to perceive and act in real environments...

--------------------------------------------------------------------------------
Chunks Retrieved: 5

📚 SOURCES:
  1. Introduction to Physical AI
     Module: module-01
     URL: https://site.com/docs/module-01/chapter-01
     Relevance: 0.856
```

### Example 2: Interactive Chat

```bash
python rag_agent.py --interactive
```

**Conversation:**
```
You: What is physical AI?