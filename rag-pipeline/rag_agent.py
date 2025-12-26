#!/usr/bin/env python3
"""
RAG Agent using OpenAI Agents SDK

This agent integrates with the Qdrant vector database to provide
intelligent retrieval-augmented generation for the Physical AI book.

Features:
- Query understanding and reformulation
- Vector database retrieval from Qdrant
- Context-aware response generation
- Multi-turn conversation support with session memory
- Built-in tracing and usage tracking
"""

import os
import sys
import asyncio
from typing import List, Dict, Optional
from dotenv import load_dotenv

# OpenAI Agents SDK imports (official)
from agents import (
    Agent,
    Runner,
    function_tool,
    ModelSettings,
    SQLiteSession,
    trace,
    set_default_openai_key
)

# RAG pipeline imports
import cohere
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

# Load environment variables
load_dotenv()

# Global configuration (for function tools)
_cohere_client = None
_qdrant_client = None
_collection_name = None


class RAGAgent:
    """
    RAG Agent that combines OpenAI Agents SDK with Qdrant retrieval.

    This agent can:
    1. Accept user queries about Physical AI
    2. Retrieve relevant content from Qdrant vector database
    3. Generate accurate, context-aware responses
    4. Maintain conversation history with sessions
    5. Track usage and provide tracing
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        cohere_api_key: Optional[str] = None,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        collection_name: str = "physical_ai_book",
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        Initialize the RAG Agent.

        Args:
            openai_api_key: OpenAI API key (defaults to env var)
            cohere_api_key: Cohere API key for embeddings (defaults to env var)
            qdrant_url: Qdrant cluster URL (defaults to env var)
            qdrant_api_key: Qdrant API key (defaults to env var)
            collection_name: Name of Qdrant collection
            model: OpenAI model to use for generation
            temperature: Model temperature (0-1)
            max_tokens: Maximum tokens in response
        """
        global _cohere_client, _qdrant_client, _collection_name

        # Load API keys from environment if not provided
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.cohere_api_key = cohere_api_key or os.getenv("COHERE_API_KEY")
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_URL")
        self.qdrant_api_key = qdrant_api_key or os.getenv("QDRANT_API_KEY")
        self.collection_name = collection_name
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Validate required credentials
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required. Set it in .env or pass as argument")
        if not self.cohere_api_key:
            raise ValueError("COHERE_API_KEY is required. Set it in .env or pass as argument")
        if not self.qdrant_url or not self.qdrant_api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY are required. Set them in .env or pass as arguments")

        # Set OpenAI API key globally for the SDK
        set_default_openai_key(self.openai_api_key, use_for_tracing=True)

        # Initialize clients (store globally for function tools to access)
        _cohere_client = cohere.Client(self.cohere_api_key)
        _qdrant_client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key
        )
        _collection_name = self.collection_name

        # Store for instance access
        self.cohere_client = _cohere_client
        self.qdrant_client = _qdrant_client

        # Create the agent using OpenAI Agents SDK
        self.agent = self._create_agent()

        print(f"✓ RAG Agent initialized")
        print(f"  Model: {self.model}")
        print(f"  Collection: {self.collection_name}")

    def _create_agent(self) -> Agent:
        """
        Create an Agent using OpenAI Agents SDK.

        Returns:
            Agent object with RAG capabilities
        """
        agent = Agent(
            name="Physical AI RAG Assistant",
            instructions="""You are an expert assistant for the Physical AI educational book.
Your role is to help users learn about physical AI, robotics, simulation, and related topics.

When answering questions:
1. ALWAYS use the retrieve_context tool first to get relevant information from the book
2. Base your answers on the retrieved context
3. Cite specific sections or modules when relevant (e.g., "According to Module 02...")
4. If information is not in the retrieved context, say so clearly
5. Provide helpful examples and explanations
6. Be concise but comprehensive

The book covers:
- Module 01: Introduction to Physical AI and sensors
- Module 02: Simulation tools (Gazebo, Unity), digital twins, physics simulation
- Module 03: ROS (Robot Operating System)
- Module 04: Advanced topics

Always maintain a helpful, educational tone.""",
            model_settings=ModelSettings(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            ),
            tools=[retrieve_context_tool]
        )

        return agent

    def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        module_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve relevant context from Qdrant vector database.

        Args:
            query: User query
            top_k: Number of chunks to retrieve
            module_filter: Optional module filter (e.g., "module-01")

        Returns:
            List of retrieved chunks with metadata and scores
        """
        # Generate query embedding using Cohere
        response = self.cohere_client.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query"  # Important: search_query for queries
        )
        query_embedding = response.embeddings[0]

        # Build filter if module specified
        query_filter = None
        if module_filter:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="module",
                        match=MatchValue(value=module_filter)
                    )
                ]
            )

        # Search Qdrant
        results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
            with_vectors=False
        )

        # Format results
        chunks = []
        for result in results:
            chunks.append({
                'text': result.payload.get('text', ''),
                'url': result.payload.get('url', ''),
                'title': result.payload.get('title', ''),
                'module': result.payload.get('module'),
                'heading_hierarchy': result.payload.get('heading_hierarchy', ''),
                'score': result.score,
                'chunk_id': result.payload.get('chunk_id', ''),
            })

        return chunks

    def query(
        self,
        user_query: str,
        session_id: Optional[str] = None,
        use_tracing: bool = False
    ) -> Dict:
        """
        Process a user query and generate a response.

        Args:
            user_query: User's question
            session_id: Optional session ID for conversation history
            use_tracing: Enable tracing for debugging

        Returns:
            Dict with response and metadata
        """
        print(f"\n🔍 Processing query: '{user_query}'")

        # Create session if session_id provided
        session = None
        if session_id:
            session = SQLiteSession(session_id, "conversations.db")

        # Run with or without tracing
        if use_tracing:
            with trace("RAG Query", group_id=session_id):
                result = Runner.run_sync(
                    self.agent,
                    user_query,
                    session=session
                )
        else:
            result = Runner.run_sync(
                self.agent,
                user_query,
                session=session
            )

        print("✓ Response generated\n")

        # Extract usage statistics
        usage = result.context_wrapper.usage if hasattr(result, 'context_wrapper') else None

        response_data = {
            'query': user_query,
            'response': result.final_output,
            'conversation_items': len(result.new_items)
        }

        # Add usage stats if available
        if usage:
            response_data['usage'] = {
                'requests': usage.requests,
                'input_tokens': usage.input_tokens,
                'output_tokens': usage.output_tokens,
                'total_tokens': usage.total_tokens
            }

        return response_data

    async def query_async(
        self,
        user_query: str,
        session_id: Optional[str] = None,
        use_tracing: bool = False
    ) -> Dict:
        """
        Process a user query asynchronously.

        Args:
            user_query: User's question
            session_id: Optional session ID for conversation history
            use_tracing: Enable tracing for debugging

        Returns:
            Dict with response and metadata
        """
        print(f"\n🔍 Processing query: '{user_query}'")

        # Create session if session_id provided
        session = None
        if session_id:
            session = SQLiteSession(session_id, "conversations.db")

        # Run with or without tracing
        if use_tracing:
            with trace("RAG Query", group_id=session_id):
                result = await Runner.run(
                    self.agent,
                    user_query,
                    session=session
                )
        else:
            result = await Runner.run(
                self.agent,
                user_query,
                session=session
            )

        print("✓ Response generated\n")

        # Extract usage statistics
        usage = result.context_wrapper.usage if hasattr(result, 'context_wrapper') else None

        response_data = {
            'query': user_query,
            'response': result.final_output,
            'conversation_items': len(result.new_items)
        }

        # Add usage stats if available
        if usage:
            response_data['usage'] = {
                'requests': usage.requests,
                'input_tokens': usage.input_tokens,
                'output_tokens': usage.output_tokens,
                'total_tokens': usage.total_tokens
            }

        return response_data


# Define retrieval tool using @function_tool decorator
@function_tool
def retrieve_context_tool(query: str, top_k: int = 5) -> str:
    """
    Retrieve relevant content from the Physical AI book using vector search.

    This tool searches the book's vector database for content relevant to the user's query.
    ALWAYS use this tool before answering questions about Physical AI topics.

    Args:
        query: The search query or topic to find information about
        top_k: Number of relevant chunks to retrieve (default: 5, max: 10)

    Returns:
        Formatted context from the book with sources and relevance scores
    """
    global _cohere_client, _qdrant_client, _collection_name

    if not _cohere_client or not _qdrant_client:
        return "Error: Retrieval system not initialized"

    try:
        # Limit top_k
        top_k = min(top_k, 10)

        # Generate query embedding
        response = _cohere_client.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query"
        )
        query_embedding = response.embeddings[0]

        # Search Qdrant
        results = _qdrant_client.search(
            collection_name=_collection_name,
            query_vector=query_embedding,
            limit=top_k,
            with_payload=True,
            with_vectors=False
        )

        if not results:
            return "No relevant content found in the book for this query."

        # Format context
        context_parts = ["RETRIEVED CONTEXT FROM PHYSICAL AI BOOK:\n"]

        for i, result in enumerate(results, 1):
            payload = result.payload
            context_parts.append(f"\n[Source {i}]")
            context_parts.append(f"Title: {payload.get('title', 'N/A')}")

            if payload.get('module'):
                context_parts.append(f"Module: {payload['module']}")

            if payload.get('heading_hierarchy'):
                context_parts.append(f"Section: {payload['heading_hierarchy']}")

            context_parts.append(f"Relevance Score: {result.score:.3f}")
            context_parts.append(f"URL: {payload.get('url', 'N/A')}")
            context_parts.append(f"\nContent:\n{payload.get('text', '')}")
            context_parts.append("\n" + "-" * 80)

        return "\n".join(context_parts)

    except Exception as e:
        return f"Error retrieving context: {str(e)}"


def main():
    """
    Demo script showing RAG Agent usage with session support.
    """
    import argparse

    parser = argparse.ArgumentParser(description="RAG Agent for Physical AI Book")
    parser.add_argument("--query", type=str, help="Single query to ask")
    parser.add_argument("--interactive", action="store_true", help="Interactive chat mode")
    parser.add_argument("--async-mode", action="store_true", help="Use async execution")
    parser.add_argument("--session-id", type=str, help="Session ID for conversation history")
    parser.add_argument("--trace", action="store_true", help="Enable tracing")
    parser.add_argument("--show-usage", action="store_true", help="Show token usage statistics")

    args = parser.parse_args()

    # Initialize agent
    print("Initializing RAG Agent...")
    try:
        agent = RAGAgent()
    except Exception as e:
        print(f"Error initializing agent: {e}")
        sys.exit(1)

    if args.interactive:
        # Interactive mode with session support
        print("\n" + "=" * 80)
        print("RAG AGENT - INTERACTIVE MODE")
        print("=" * 80)
        if args.session_id:
            print(f"Session ID: {args.session_id} (conversation history enabled)")
        print("Ask questions about Physical AI. Type 'exit' to quit.\n")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break

            if not user_input:
                continue

            try:
                if args.async_mode:
                    # Async execution
                    result = asyncio.run(agent.query_async(
                        user_input,
                        session_id=args.session_id,
                        use_tracing=args.trace
                    ))
                else:
                    # Sync execution
                    result = agent.query(
                        user_input,
                        session_id=args.session_id,
                        use_tracing=args.trace
                    )

                print(f"\nAssistant: {result['response']}\n")

                # Show usage if requested
                if args.show_usage and 'usage' in result:
                    usage = result['usage']
                    print(f"📊 Usage: {usage['total_tokens']} tokens "
                          f"({usage['input_tokens']} in, {usage['output_tokens']} out)\n")

            except Exception as e:
                print(f"\n❌ Error: {e}\n")

    elif args.query:
        # Single query mode
        try:
            if args.async_mode:
                result = asyncio.run(agent.query_async(
                    args.query,
                    session_id=args.session_id,
                    use_tracing=args.trace
                ))
            else:
                result = agent.query(
                    args.query,
                    session_id=args.session_id,
                    use_tracing=args.trace
                )

            print("=" * 80)
            print(f"QUERY: {result['query']}")
            print("=" * 80)
            print(f"\nRESPONSE:\n{result['response']}\n")
            print("-" * 80)

            # Show usage if available
            if 'usage' in result:
                usage = result['usage']
                print(f"\n📊 USAGE STATISTICS")
                print(f"Requests: {usage['requests']}")
                print(f"Input tokens: {usage['input_tokens']}")
                print(f"Output tokens: {usage['output_tokens']}")
                print(f"Total tokens: {usage['total_tokens']}\n")

        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    else:
        # Default: show help
        parser.print_help()


if __name__ == "__main__":
    main()
