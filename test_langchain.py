#!/usr/bin/env python3
"""
AI Action Ledger - LangChain Integration Test

This script tests the LangChain callback with a real LangChain agent.

Prerequisites:
- AI Action Ledger running: docker compose up
- Install dependencies: pip install requests langchain langchain-community
- Set OPENAI_API_KEY environment variable (or use fake LLM below)

Usage:
    python test_langchain.py
"""

import os
import sys
import time
import requests

# Add SDK to path (for local testing)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration
LEDGER_URL = "http://localhost:8000"
API_KEY = "dev-api-key-change-me"
AGENT_ID = f"langchain-test-{int(time.time())}"

def check_ledger():
    """Check if ledger is running."""
    try:
        response = requests.get(f"{LEDGER_URL}/health")
        return response.status_code == 200
    except:
        return False

def verify_chain(agent_id):
    """Verify the chain after test."""
    response = requests.get(
        f"{LEDGER_URL}/verify",
        headers={"X-API-Key": API_KEY},
        params={"agent_id": agent_id}
    )
    return response.json()

def list_events(agent_id):
    """List events for agent."""
    response = requests.get(
        f"{LEDGER_URL}/events",
        headers={"X-API-Key": API_KEY},
        params={"agent_id": agent_id}
    )
    return response.json()

def test_with_fake_llm():
    """Test with a fake LLM (no API key needed)."""
    print("\n[Test 1] Testing with FakeLLM (no API key needed)...")
    
    try:
        from langchain_community.llms.fake import FakeListLLM
        from action_ledger import ActionLedgerCallback
    except ImportError as e:
        print(f"  ERROR: Missing dependency: {e}")
        print("  Run: pip install langchain langchain-community")
        return False
    
    # Create callback
    callback = ActionLedgerCallback(
        ledger_url=LEDGER_URL,
        api_key=API_KEY,
        agent_id=AGENT_ID,
        environment="test"
    )
    
    # Create fake LLM with predetermined responses
    llm = FakeListLLM(
        responses=[
            "The capital of France is Paris.",
            "Python is a programming language.",
            "42 is the answer to everything."
        ],
        callbacks=[callback]
    )
    
    # Make calls
    prompts = [
        "What is the capital of France?",
        "What is Python?",
        "What is the meaning of life?"
    ]
    
    for prompt in prompts:
        print(f"  Prompt: {prompt[:40]}...")
        response = llm.invoke(prompt)
        print(f"  Response: {response[:40]}...")
    
    return True

def test_with_openai():
    """Test with real OpenAI (requires API key)."""
    print("\n[Test 2] Testing with OpenAI...")
    
    if not os.environ.get("OPENAI_API_KEY"):
        print("  SKIPPED: No OPENAI_API_KEY set")
        return None
    
    try:
        from langchain_openai import OpenAI
        from action_ledger import ActionLedgerCallback
    except ImportError as e:
        print(f"  ERROR: Missing dependency: {e}")
        print("  Run: pip install langchain-openai")
        return False
    
    agent_id = f"openai-test-{int(time.time())}"
    
    callback = ActionLedgerCallback(
        ledger_url=LEDGER_URL,
        api_key=API_KEY,
        agent_id=agent_id,
        environment="test"
    )
    
    llm = OpenAI(
        temperature=0,
        max_tokens=50,
        callbacks=[callback]
    )
    
    print("  Prompt: What is 2+2?")
    response = llm.invoke("What is 2+2? Answer in one word.")
    print(f"  Response: {response.strip()}")
    
    return agent_id

def main():
    print("=" * 60)
    print("AI Action Ledger - LangChain Integration Test")
    print("=" * 60)
    
    # Check ledger is running
    print("\n[Setup] Checking ledger...")
    if not check_ledger():
        print("  ERROR: Ledger not running!")
        print("  Run: cd ai-action-ledger && docker compose up")
        return
    print("  Ledger is healthy ✓")
    
    # Run fake LLM test
    fake_success = test_with_fake_llm()
    
    # Run OpenAI test (if key available)
    openai_agent = test_with_openai()
    
    # Verify results
    print("\n[Verification]")
    print("-" * 40)
    
    if fake_success:
        verification = verify_chain(AGENT_ID)
        events = list_events(AGENT_ID)
        print(f"  FakeLLM Agent: {AGENT_ID}")
        print(f"    Events logged: {events['total']}")
        print(f"    Chain valid: {verification['is_valid']}")
        
        if events['total'] > 0:
            print("    Event types logged:")
            for event in events['events'][:5]:
                print(f"      - {event['action_type']}")
    
    if openai_agent:
        verification = verify_chain(openai_agent)
        events = list_events(openai_agent)
        print(f"\n  OpenAI Agent: {openai_agent}")
        print(f"    Events logged: {events['total']}")
        print(f"    Chain valid: {verification['is_valid']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  FakeLLM test: {'PASSED ✓' if fake_success else 'FAILED ✗'}")
    if openai_agent is None:
        print(f"  OpenAI test:  SKIPPED (no API key)")
    elif openai_agent:
        print(f"  OpenAI test:  PASSED ✓")
    else:
        print(f"  OpenAI test:  FAILED ✗")
    
    print(f"\n  Dashboard: http://localhost:3000")
    print("=" * 60)

if __name__ == "__main__":
    main()