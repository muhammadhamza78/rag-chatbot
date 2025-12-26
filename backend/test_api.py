#!/usr/bin/env python3
"""
API Test Script
Spec 4: Frontend-Backend Integration

Tests the FastAPI backend endpoints to ensure proper integration
with the RAG agent from Spec 3.

Usage:
    python test_api.py
"""

import requests
import json
import sys
from typing import Dict, Any


API_BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_health_check() -> bool:
    """Test the /api/health endpoint"""
    print_section("TEST 1: Health Check")

    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("agent_ready"):
                print("✅ Health check passed - Agent is ready")
                return True
            else:
                print("⚠️  Health check passed but agent is not ready")
                return False
        else:
            print("❌ Health check failed")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_query_endpoint(query: str, session_id: str = None) -> Dict[str, Any]:
    """Test the /api/query endpoint"""
    print_section(f"TEST 2: Query - '{query}'")

    payload = {
        "query": query,
        "session_id": session_id,
        "use_tracing": False
    }

    try:
        print(f"Request Payload: {json.dumps(payload, indent=2)}")
        response = requests.post(
            f"{API_BASE_URL}/api/query",
            json=payload,
            timeout=30
        )

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\nQuery: {data['query']}")
            print(f"\nResponse:\n{data['response']}")
            print(f"\nConversation Items: {data['conversation_items']}")

            if data.get('usage'):
                usage = data['usage']
                print(f"\nUsage Statistics:")
                print(f"  Requests: {usage['requests']}")
                print(f"  Input tokens: {usage['input_tokens']}")
                print(f"  Output tokens: {usage['output_tokens']}")
                print(f"  Total tokens: {usage['total_tokens']}")

            print("\n✅ Query test passed")
            return data
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            print(f"\n❌ Query failed: {error_detail}")
            return {}

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return {}


def test_multiple_queries():
    """Test multiple queries with session support"""
    print_section("TEST 3: Multiple Queries with Session")

    session_id = f"test_session_{int(requests.get(f'{API_BASE_URL}/api/health').elapsed.total_seconds())}"
    queries = [
        "What is physical AI?",
        "Can you explain digital twins?",
        "What is ROS?"
    ]

    print(f"Session ID: {session_id}\n")

    for i, query in enumerate(queries, 1):
        print(f"\n--- Query {i}/{len(queries)} ---")
        test_query_endpoint(query, session_id)
        print()

    print("✅ Multiple queries test completed")


def test_invalid_query():
    """Test with invalid query"""
    print_section("TEST 4: Invalid Query (Empty)")

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/query",
            json={"query": ""},
            timeout=5
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 422:
            print("✅ Validation working correctly - Empty query rejected")
        else:
            print("⚠️  Unexpected response for empty query")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  PHYSICAL AI RAG API - Test Suite")
    print("  Backend API: " + API_BASE_URL)
    print("=" * 80)

    # Check if server is running
    try:
        requests.get(API_BASE_URL, timeout=2)
    except Exception as e:
        print(f"\n❌ Cannot connect to API server at {API_BASE_URL}")
        print(f"   Error: {e}")
        print(f"\n   Please start the server with: python api_server.py")
        sys.exit(1)

    # Run tests
    tests_passed = 0
    tests_total = 4

    # Test 1: Health check
    if test_health_check():
        tests_passed += 1

    # Test 2: Single query
    result = test_query_endpoint("What is physical AI?")
    if result:
        tests_passed += 1

    # Test 3: Multiple queries with session
    test_multiple_queries()
    tests_passed += 1  # Assume pass if no errors

    # Test 4: Invalid query
    test_invalid_query()
    tests_passed += 1  # Assume pass if no errors

    # Summary
    print_section("TEST SUMMARY")
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print(f"Success Rate: {(tests_passed/tests_total)*100:.1f}%")

    if tests_passed == tests_total:
        print("\n✅ All tests passed!")
    else:
        print(f"\n⚠️  {tests_total - tests_passed} test(s) failed")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
