import React, { useState, useRef, useEffect } from 'react';
import styles from './styles.module.css';

/**
 * RAG Chat Component
 * Spec 4: Frontend-Backend Integration
 *
 * Interactive chat interface for querying the Physical AI RAG agent.
 * Communicates with the FastAPI backend to retrieve AI-generated responses.
 */

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface QueryResponse {
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

const RAGChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState<string>(() => `session_${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Backend API URL (configurable via environment variable)
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Auto-scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  /**
   * Send query to RAG agent backend
   */
  const sendQuery = async (query: string) => {
    if (!query.trim()) return;

    // Add user message to chat
    const userMessage: Message = {
      role: 'user',
      content: query,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      // Call backend API
      const response = await fetch(`${API_URL}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          session_id: sessionId,
          use_tracing: false
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: QueryResponse = await response.json();

      // Add assistant message to chat
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      console.error('Error querying RAG agent:', err);
      setError(err instanceof Error ? err.message : 'Failed to get response');

      // Add error message to chat
      const errorMessage: Message = {
        role: 'assistant',
        content: `❌ Error: ${err instanceof Error ? err.message : 'Failed to get response'}. Please ensure the backend server is running on ${API_URL}.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle form submission
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendQuery(input);
  };

  /**
   * Handle example question click
   */
  const handleExampleClick = (question: string) => {
    setInput(question);
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.chatHeader}>
        <h2>💬 Ask about Physical AI</h2>
        <p>Powered by RAG Agent with OpenAI Agents SDK</p>
      </div>

      {/* Example questions */}
      {messages.length === 0 && (
        <div className={styles.examplesContainer}>
          <h3>Try asking:</h3>
          <div className={styles.exampleButtons}>
            <button
              className={styles.exampleButton}
              onClick={() => handleExampleClick('What is physical AI?')}
            >
              What is physical AI?
            </button>
            <button
              className={styles.exampleButton}
              onClick={() => handleExampleClick('Explain digital twins in simulation')}
            >
              Explain digital twins in simulation
            </button>
            <button
              className={styles.exampleButton}
              onClick={() => handleExampleClick('What is ROS and how is it used?')}
            >
              What is ROS and how is it used?
            </button>
            <button
              className={styles.exampleButton}
              onClick={() => handleExampleClick('How do sensors work in robotics?')}
            >
              How do sensors work in robotics?
            </button>
          </div>
        </div>
      )}

      {/* Messages display */}
      <div className={styles.messagesContainer}>
        {messages.map((message, index) => (
          <div
            key={index}
            className={`${styles.message} ${
              message.role === 'user' ? styles.userMessage : styles.assistantMessage
            }`}
          >
            <div className={styles.messageRole}>
              {message.role === 'user' ? '👤 You' : '🤖 AI Assistant'}
            </div>
            <div className={styles.messageContent}>{message.content}</div>
            <div className={styles.messageTimestamp}>
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
        {loading && (
          <div className={`${styles.message} ${styles.assistantMessage}`}>
            <div className={styles.messageRole}>🤖 AI Assistant</div>
            <div className={styles.messageContent}>
              <div className={styles.loadingDots}>
                <span>.</span>
                <span>.</span>
                <span>.</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input form */}
      <form onSubmit={handleSubmit} className={styles.inputForm}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about Physical AI..."
          className={styles.input}
          disabled={loading}
        />
        <button
          type="submit"
          className={styles.sendButton}
          disabled={loading || !input.trim()}
        >
          {loading ? '...' : 'Send'}
        </button>
      </form>

      {/* Error display */}
      {error && (
        <div className={styles.errorBanner}>
          ⚠️ {error}
        </div>
      )}
    </div>
  );
};

export default RAGChat;
