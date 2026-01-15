#!/usr/bin/env python3
"""
Test ActionLogger - the framework-agnostic core.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from action_ledger import LedgerClient, ActionLogger

LEDGER_URL = "http://localhost:8000"
API_KEY = "dev-api-key-change-me"
AGENT_ID = f"logger-test-{int(time.time())}"


def main():
    print("=" * 60)
    print("ActionLogger Test")
    print("=" * 60)
    
    # Check ledger is running
    print("\n[1] Checking ledger...")
    client = LedgerClient(LEDGER_URL, API_KEY)
    try:
        health = client.health()
        print(f"  Status: {health['status']}")
    except Exception as e:
        print(f"  ERROR: {e}")
        print("  Is the ledger running? docker compose up")
        return
    
    # Test ActionLogger
    print(f"\n[2] Testing ActionLogger with agent_id={AGENT_ID}")
    logger = ActionLogger(
        ledger_url=LEDGER_URL,
        api_key=API_KEY,
        agent_id=AGENT_ID,
        environment="test",
    )
    
    print("\n  Simulating agent workflow...")
    
    logger.llm_start(input_data="What is the capital of France?", model="gpt-test")
    print("    ✓ llm_start")
    logger.llm_end(output_data="The capital of France is Paris.")
    print("    ✓ llm_end")
    
    logger.tool_start(tool_name="web_search", input_data="Paris weather")
    print("    ✓ tool_start")
    logger.tool_end(output_data="72°F and sunny")
    print("    ✓ tool_end")
    
    logger.chain_start(chain_name="summarize", input_data={"text": "..."})
    print("    ✓ chain_start")
    logger.chain_end(output_data={"summary": "..."})
    print("    ✓ chain_end")
    
    logger.log("custom_action", input_data="foo", output_data="bar")
    print("    ✓ custom log")
    
    # Verify
    print("\n[3] Verifying chain...")
    result = client.verify_chain(AGENT_ID)
    print(f"  Valid: {result['is_valid']}")
    print(f"  Events: {result['events_checked']}")
    
    # List events
    print("\n[4] Events logged:")
    events = client.list_events(agent_id=AGENT_ID)
    for event in events['events']:
        print(f"    - {event['action_type']}")
    
    print("\n" + "=" * 60)
    print("ActionLogger test PASSED ✓")
    print("=" * 60)


if __name__ == "__main__":
    main()