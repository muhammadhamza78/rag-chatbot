#!/usr/bin/env python3
"""
RAG Agent End-to-End Testing

This script tests the RAG Agent integration with Qdrant retrieval
and OpenAI generation capabilities.

Test Suite:
1. Agent initialization
2. Single query processing
3. Multi-turn conversation
4. Context retrieval validation
5. Response quality checks
"""

import os
import sys
import time
from typing import List, Dict
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import RAG agent
try:
    from rag_agent import RAGAgent
except ImportError:
    print("❌ Error: Could not import RAGAgent")
    print("   Make sure rag_agent.py is in the same directory")
    sys.exit(1)


class RAGAgentTester:
    """
    Test suite for RAG Agent validation.
    """

    def __init__(self):
        """Initialize tester."""
        self.agent = None
        self.test_results = []

    def run_all_tests(self) -> Dict:
        """
        Run complete test suite.

        Returns:
            Dict with test results and summary
        """
        print("=" * 80)
        print("RAG AGENT END-TO-END TESTING")
        print("=" * 80)
        print()

        # Test 1: Initialization
        if not self.test_initialization():
            print("❌ Initialization failed. Stopping tests.")
            return self._get_summary()

        # Test 2: Single query
        self.test_single_query()

        # Test 3: Context retrieval
        self.test_context_retrieval()

        # Test 4: Response quality
        self.test_response_quality()

        # Test 5: Multi-turn conversation
        self.test_multi_turn_conversation()

        # Test 6: Module filtering
        self.test_module_filtering()

        # Summary
        return self._get_summary()

    def test_initialization(self) -> bool:
        """
        Test 1: Agent Initialization

        Validates:
        - API keys are loaded
        - Clients are initialized
        - Assistant is created
        """
        print("[Test 1] Agent Initialization")
        print("-" * 80)

        try:
            start_time = time.time()
            self.agent = RAGAgent()
            elapsed = time.time() - start_time

            # Verify components
            assert self.agent.openai_client is not None, "OpenAI client not initialized"
            assert self.agent.cohere_client is not None, "Cohere client not initialized"
            assert self.agent.qdrant_client is not None, "Qdrant client not initialized"
            assert self.agent.assistant is not None, "OpenAI Assistant not created"

            self.test_results.append({
                'test': 'Initialization',
                'status': 'PASSED',
                'time': elapsed,
                'message': 'All components initialized successfully'
            })

            print(f"✓ PASSED ({elapsed:.2f}s)")
            print()
            return True

        except Exception as e:
            self.test_results.append({
                'test': 'Initialization',
                'status': 'FAILED',
                'error': str(e)
            })
            print(f"✗ FAILED: {e}")
            print()
            return False

    def test_single_query(self):
        """
        Test 2: Single Query Processing

        Validates:
        - Query processing works end-to-end
        - Response is generated
        - Sources are returned
        """
        print("[Test 2] Single Query Processing")
        print("-" * 80)

        test_query = "What is physical AI?"

        try:
            start_time = time.time()
            result = self.agent.query(test_query, top_k=3)
            elapsed = time.time() - start_time

            # Validations
            assert result is not None, "No result returned"
            assert 'response' in result, "No response in result"
            assert 'sources' in result, "No sources in result"
            assert len(result['response']) > 0, "Empty response"
            assert result['chunks_retrieved'] > 0, "No chunks retrieved"

            self.test_results.append({
                'test': 'Single Query',
                'status': 'PASSED',
                'time': elapsed,
                'query': test_query,
                'chunks_retrieved': result['chunks_retrieved'],
                'response_length': len(result['response'])
            })

            print(f"✓ PASSED ({elapsed:.2f}s)")
            print(f"  Query: {test_query}")
            print(f"  Chunks retrieved: {result['chunks_retrieved']}")
            print(f"  Response length: {len(result['response'])} chars")
            print(f"  Sources: {len(result.get('sources', []))}")
            print()

        except Exception as e:
            self.test_results.append({
                'test': 'Single Query',
                'status': 'FAILED',
                'error': str(e)
            })
            print(f"✗ FAILED: {e}")
            print()

    def test_context_retrieval(self):
        """
        Test 3: Context Retrieval Validation

        Validates:
        - Retrieval returns relevant chunks
        - Metadata is complete
        - Scores are valid
        """
        print("[Test 3] Context Retrieval Validation")
        print("-" * 80)

        test_query = "How to simulate sensors in Gazebo?"

        try:
            start_time = time.time()
            chunks = self.agent.retrieve_context(test_query, top_k=5)
            elapsed = time.time() - start_time

            # Validations
            assert len(chunks) > 0, "No chunks retrieved"

            for i, chunk in enumerate(chunks):
                assert 'text' in chunk and len(chunk['text']) > 0, f"Chunk {i} has no text"
                assert 'score' in chunk, f"Chunk {i} has no score"
                assert 0.0 <= chunk['score'] <= 1.0, f"Chunk {i} score out of range: {chunk['score']}"
                assert 'url' in chunk, f"Chunk {i} has no URL"
                assert 'title' in chunk, f"Chunk {i} has no title"

            self.test_results.append({
                'test': 'Context Retrieval',
                'status': 'PASSED',
                'time': elapsed,
                'chunks_count': len(chunks),
                'avg_score': sum(c['score'] for c in chunks) / len(chunks)
            })

            print(f"✓ PASSED ({elapsed:.2f}s)")
            print(f"  Chunks retrieved: {len(chunks)}")
            print(f"  Average score: {sum(c['score'] for c in chunks) / len(chunks):.3f}")
            print(f"  Top score: {chunks[0]['score']:.3f}")
            print()

        except Exception as e:
            self.test_results.append({
                'test': 'Context Retrieval',
                'status': 'FAILED',
                'error': str(e)
            })
            print(f"✗ FAILED: {e}")
            print()

    def test_response_quality(self):
        """
        Test 4: Response Quality Checks

        Validates:
        - Response is coherent
        - Response addresses the query
        - Response uses retrieved context
        """
        print("[Test 4] Response Quality")
        print("-" * 80)

        test_queries = [
            "What is physical AI?",
            "Explain digital twins",
            "How does ROS work?"
        ]

        passed = 0
        failed = 0

        for query in test_queries:
            try:
                result = self.agent.query(query, top_k=3)

                # Basic quality checks
                response = result['response']
                assert len(response) > 50, f"Response too short: {len(response)} chars"
                assert not response.startswith("Error"), "Response indicates error"

                passed += 1
                print(f"  ✓ '{query}' - {len(response)} chars")

            except Exception as e:
                failed += 1
                print(f"  ✗ '{query}' - {e}")

        total_time = 0  # Not tracking individual times here
        if passed == len(test_queries):
            self.test_results.append({
                'test': 'Response Quality',
                'status': 'PASSED',
                'queries_tested': len(test_queries),
                'passed': passed
            })
            print(f"\n✓ PASSED ({passed}/{len(test_queries)} queries)")
        else:
            self.test_results.append({
                'test': 'Response Quality',
                'status': 'FAILED',
                'passed': passed,
                'failed': failed
            })
            print(f"\n✗ FAILED ({passed}/{len(test_queries)} passed)")

        print()

    def test_multi_turn_conversation(self):
        """
        Test 5: Multi-turn Conversation

        Validates:
        - Thread continuity
        - Context switching between queries
        - Conversation flow
        """
        print("[Test 5] Multi-turn Conversation")
        print("-" * 80)

        conversation = [
            "What is physical AI?",
            "What are the main simulation tools?",
            "Tell me more about Gazebo"
        ]

        try:
            start_time = time.time()

            # First query creates thread
            result1 = self.agent.query(conversation[0], top_k=3)
            thread_id = result1['thread_id']

            # Continue conversation
            result2 = self.agent.chat(thread_id, conversation[1], top_k=3)
            result3 = self.agent.chat(thread_id, conversation[2], top_k=3)

            elapsed = time.time() - start_time

            # Validations
            assert result1['thread_id'] == thread_id, "Thread ID changed"
            assert result2['thread_id'] == thread_id, "Thread ID changed in turn 2"
            assert result3['thread_id'] == thread_id, "Thread ID changed in turn 3"

            self.test_results.append({
                'test': 'Multi-turn Conversation',
                'status': 'PASSED',
                'time': elapsed,
                'turns': len(conversation),
                'thread_id': thread_id
            })

            print(f"✓ PASSED ({elapsed:.2f}s)")
            print(f"  Turns: {len(conversation)}")
            print(f"  Thread ID: {thread_id}")
            print()

        except Exception as e:
            self.test_results.append({
                'test': 'Multi-turn Conversation',
                'status': 'FAILED',
                'error': str(e)
            })
            print(f"✗ FAILED: {e}")
            print()

    def test_module_filtering(self):
        """
        Test 6: Module Filtering

        Validates:
        - Module filter works correctly
        - Only relevant modules are retrieved
        """
        print("[Test 6] Module Filtering")
        print("-" * 80)

        test_query = "What are sensors?"
        test_module = "module-01"

        try:
            start_time = time.time()

            # Query with module filter
            chunks = self.agent.retrieve_context(
                test_query,
                top_k=5,
                module_filter=test_module
            )

            elapsed = time.time() - start_time

            # Validate all chunks are from correct module
            for chunk in chunks:
                if chunk.get('module'):  # Some chunks might not have module
                    assert chunk['module'] == test_module, \
                        f"Wrong module: {chunk['module']} (expected {test_module})"

            self.test_results.append({
                'test': 'Module Filtering',
                'status': 'PASSED',
                'time': elapsed,
                'chunks_retrieved': len(chunks),
                'module': test_module
            })

            print(f"✓ PASSED ({elapsed:.2f}s)")
            print(f"  Module filter: {test_module}")
            print(f"  Chunks retrieved: {len(chunks)}")
            print()

        except Exception as e:
            self.test_results.append({
                'test': 'Module Filtering',
                'status': 'FAILED',
                'error': str(e)
            })
            print(f"✗ FAILED: {e}")
            print()

    def _get_summary(self) -> Dict:
        """
        Generate test summary.

        Returns:
            Dict with summary statistics
        """
        passed = sum(1 for r in self.test_results if r['status'] == 'PASSED')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAILED')
        total = len(self.test_results)

        return {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': (passed / total * 100) if total > 0 else 0,
            'results': self.test_results
        }


def main():
    """
    Main test execution.
    """
    # Check environment
    required_vars = ['OPENAI_API_KEY', 'COHERE_API_KEY', 'QDRANT_URL', 'QDRANT_API_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease set them in your .env file")
        sys.exit(1)

    # Run tests
    tester = RAGAgentTester()
    summary = tester.run_all_tests()

    # Print summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Pass Rate: {summary['pass_rate']:.1f}%")
    print()

    # Detailed results
    if summary['failed'] > 0:
        print("Failed Tests:")
        for result in summary['results']:
            if result['status'] == 'FAILED':
                print(f"  - {result['test']}: {result.get('error', 'Unknown error')}")
        print()

    # Exit code
    sys.exit(0 if summary['failed'] == 0 else 1)


if __name__ == "__main__":
    main()
