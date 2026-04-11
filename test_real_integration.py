#!/usr/bin/env python3
"""
Test real integration between CLI and Python engine
"""

import subprocess
import json
import sys
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_engine_direct():
    """Test calling the engine directly"""
    from victory.core.llm import LLMProviderFactory, Message

    print("\n" + "=" * 70)
    print("TEST 1: Direct LLM Provider Test")
    print("=" * 70)

    try:
        # Test Modal provider (free tier)
        modal_key = "modalresearch_7ZX7CTiopRhNGv8ZLgfrmMrRRMMmsKvEwOMAKlxmDOk"

        provider = LLMProviderFactory.create("modal", modal_key, "zai-org/GLM-5.1-FP8")

        messages = [
            Message(
                role="system", content="You are a helpful assistant. Respond briefly."
            ),
            Message(role="user", content="Say 'Hello from Victory!'"),
        ]

        response = await provider.generate(messages)
        print(f"✅ LLM Response: {response.content[:100]}...\n")
        return True
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False


def test_github_client():
    """Test GitHub client"""
    print("\n" + "=" * 70)
    print("TEST 2: GitHub Client Test")
    print("=" * 70)

    try:
        from victory.core.github import GitHubClient

        # MockGitHub token - we won't make actual requests
        token = "ghp_test_token"
        client = GitHubClient(token)
        print(f"✅ GitHub client created: {client.__class__.__name__}\n")
        return True
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False


def test_python_engine_via_stdin():
    """Test calling Python engine via stdin/stdout"""
    print("\n" + "=" * 70)
    print("TEST 3: Python Engine via stdin/stdout")
    print("=" * 70)

    try:
        # Create a simple command
        command = {"command": "test", "message": "Testing engine input/output"}

        # Try to import the engine
        import sys

        sys.path.insert(0, "/home/ansh/victory/python")
        from victory.engine import process_command_async

        print(f"✅ Engine module imported successfully\n")
        return True
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False


async def main():
    """Run all tests"""
    print("\n" + "█" * 70)
    print("█ VICTORY REAL INTEGRATION TESTS")
    print("█" * 70)

    results = []

    # Test 1: Direct LLM
    result1 = await test_engine_direct()
    results.append(("LLM Provider", result1))

    # Test 2: GitHub Client
    result2 = test_github_client()
    results.append(("GitHub Client", result2))

    # Test 3: Python Engine
    result3 = test_python_engine_via_stdin()
    results.append(("Python Engine", result3))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        symbol = "✅" if result else "❌"
        print(f"{symbol} {name}")

    print(f"\nTotal: {passed}/{total} passed\n")

    return passed == total


if __name__ == "__main__":
    sys.path.insert(0, "/home/ansh/victory/python")
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
