# AI Action Ledger SDK

Tamper-evident audit logging for AI agent actions. One-line integration.

[![PyPI version](https://badge.fury.io/py/action-ledger.svg)](https://pypi.org/project/action-ledger/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is this?

AI Action Ledger records AI agent actions (LLM calls, tool use, chain steps) with cryptographic hash-chaining. If an event is logged, you can prove it wasn't silently changed later.

**This SDK** makes it easy to integrate with your Python applications and LangChain agents.

## Installation

```bash
pip install action-ledger
```

For LangChain integration:

```bash
pip install action-ledger[langchain]
```

## Quick Start

### Basic Usage

```python
from action_ledger import LedgerClient

client = LedgerClient(
    ledger_url="http://localhost:8000",  # or your hosted instance
    api_key="your-api-key"
)

# Log an event
event = client.log_event(
    agent_id="my-agent",
    action_type="llm_call",
    input_hash=client.hash_content("What is 2+2?"),
    output_hash=client.hash_content("4")
)
print(f"Logged: {event['event_id']}")

# Verify the chain
result = client.verify_chain("my-agent")
print(f"Chain valid: {result['is_valid']}")
```

### ActionLogger (Recommended for Custom Agents)

For custom agents or frameworks without a dedicated adapter, use `ActionLogger`. It handles hashing and errors automatically:
```python
from action_ledger import ActionLogger

logger = ActionLogger(
    ledger_url="http://localhost:8000",
    api_key="your-api-key",
    agent_id="my-agent"
)

# Log LLM calls
logger.llm_start(input_data="What is 2+2?")
logger.llm_end(output_data="4")

# Log tool usage
logger.tool_start(tool_name="calculator", input_data="2+2")
logger.tool_end(output_data="4")

# Log custom actions
logger.log("custom_action", input_data="foo", output_data="bar")
```

### Hashing Content Manually

If using `LedgerClient` directly, use the `hash_content` helper:
```python
from action_ledger import LedgerClient

client = LedgerClient("http://localhost:8000", "your-api-key")

client.log_event(
    agent_id="my-agent",
    action_type="llm_call",
    input_hash=client.hash_content("What is 2+2?"),  # SHA-256 hash
    output_hash=client.hash_content("4")
)
```

### LangChain Integration

```python
from langchain.llms import OpenAI
from action_ledger import ActionLedgerCallback

# Create callback
callback = ActionLedgerCallback(
    ledger_url="http://localhost:8000",
    api_key="your-api-key",
    agent_id="my-langchain-agent"
)

# Use with any LangChain LLM
llm = OpenAI(callbacks=[callback])
response = llm.invoke("What is 2+2?")
# Automatically logged!
```

## What Gets Logged

Each event contains:

| Field | Description |
|-------|-------------|
| `event_id` | Unique identifier (UUID) |
| `agent_id` | Which agent performed the action |
| `action_type` | Type of action (llm_call, tool_use, etc.) |
| `timestamp` | When the event occurred (UTC) |
| `input_hash` | SHA-256 hash of input |
| `output_hash` | SHA-256 hash of output |
| `event_hash` | Hash of this event |
| `previous_event_hash` | Hash of prior event (creates chain) |

**Privacy:** Raw inputs/outputs are never stored — only hashes.

## API Reference

### LedgerClient

```python
client = LedgerClient(ledger_url: str, api_key: str)

# Log an event
client.log_event(
    agent_id: str,
    action_type: str,
    input_hash: str,
    output_hash: str,
    tool_name: str = None,
    environment: str = None,
    model_version: str = None,
    prompt_version: str = None
) -> dict

# Verify chain integrity
client.verify_chain(agent_id: str) -> dict

# Hash content (helper)
client.hash_content(content: str) -> str
```

### ActionLedgerCallback (LangChain)

```python
callback = ActionLedgerCallback(
    ledger_url: str,
    api_key: str,
    agent_id: str,
    environment: str = None
)
```

Automatically logs:
- `llm_start` / `llm_end`
- `tool_start` / `tool_end`
- `chain_start` / `chain_end`

## Running the Ledger

Self-host with Docker:

```bash
git clone https://github.com/Jreamr/ai-action-ledger
cd ai-action-ledger
docker compose up --build
```

Or request hosted access: [GitHub Discussions](https://github.com/Jreamr/ai-action-ledger/discussions)

## Links

- [GitHub Repository](https://github.com/Jreamr/ai-action-ledger)
- [Documentation](https://github.com/Jreamr/ai-action-ledger/blob/main/START_HERE.md)
- [Examples](https://github.com/Jreamr/ai-action-ledger/blob/main/EXAMPLES.md)
- [Limitations](https://github.com/Jreamr/ai-action-ledger/blob/main/LIMITATIONS.md)

## License

MIT
