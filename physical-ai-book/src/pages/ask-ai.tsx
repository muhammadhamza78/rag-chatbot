import React from 'react';
import Layout from '@theme/Layout';
import RAGChat from '@site/src/components/RAGChat';

/**
 * Ask AI Page
 * Spec 4: Frontend-Backend Integration
 *
 * Dedicated page for interacting with the RAG agent.
 * Users can ask questions about Physical AI and get intelligent responses
 * powered by the OpenAI Agents SDK and Qdrant vector database.
 */

export default function AskAI() {
  return (
    <Layout
      title="Ask AI Assistant"
      description="Ask questions about Physical AI and get intelligent answers from our RAG agent"
    >
      <main style={{ padding: '2rem 0' }}>
        <div className="container">
          <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
            <h1>Ask the AI Assistant</h1>
            <p style={{ fontSize: '1.1rem', color: 'var(--ifm-color-emphasis-700)' }}>
              Get instant answers to your questions about Physical AI, robotics, simulation, and more.
              Our AI assistant is powered by a Retrieval-Augmented Generation (RAG) system that searches
              through the entire Physical AI educational book to provide accurate, contextual answers.
            </p>
          </div>

          <RAGChat />

          <div style={{ marginTop: '2rem', padding: '1.5rem', background: 'var(--ifm-color-emphasis-100)', borderRadius: '8px' }}>
            <h3>How it works</h3>
            <ol>
              <li><strong>Ask a question</strong> - Type your question about Physical AI topics</li>
              <li><strong>Vector search</strong> - The system searches through embedded book content using Qdrant</li>
              <li><strong>Context retrieval</strong> - Relevant sections are retrieved and ranked by relevance</li>
              <li><strong>AI generation</strong> - OpenAI's GPT-4o generates an answer based on retrieved context</li>
              <li><strong>Response</strong> - You receive an accurate answer with citations from the book</li>
            </ol>

            <h3 style={{ marginTop: '1.5rem' }}>Technical Stack</h3>
            <ul>
              <li><strong>Frontend:</strong> React + TypeScript (Docusaurus)</li>
              <li><strong>Backend:</strong> FastAPI + Python</li>
              <li><strong>AI Agent:</strong> OpenAI Agents SDK (gpt-4o)</li>
              <li><strong>Vector Database:</strong> Qdrant</li>
              <li><strong>Embeddings:</strong> Cohere embed-english-v3.0</li>
            </ul>
          </div>
        </div>
      </main>
    </Layout>
  );
}
