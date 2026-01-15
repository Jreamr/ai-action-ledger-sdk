"""
AI Action Ledger Client

Simple client for logging events to AI Action Ledger.
"""

import hashlib
import requests
from typing import Optional


class LedgerClient:
    """
    Low-level HTTP client for AI Action Ledger API.
    
    Use this for direct API access. For most use cases, prefer ActionLogger
    which handles hashing and error handling automatically.
    
    Example:
        client = LedgerClient("http://localhost:8000", "your-api-key")
        client.log_event(
            agent_id="my-agent",
            action_type="llm_call",
            input_hash=client.hash_content("my input"),
            output_hash=client.hash_content("my output")
        )
    """

    def __init__(self, ledger_url: str, api_key: str):
        """
        Initialize the client.

        Args:
            ledger_url: Base URL of the ledger API (e.g., "http://localhost:8000")
            api_key: API key for authentication
        """
        self.ledger_url = ledger_url.rstrip("/")
        self.api_key = api_key

    def _hash(self, content: str) -> str:
        """SHA-256 hash of content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def log_event(
        self,
        agent_id: str,
        action_type: str,
        input_hash: str,
        output_hash: str,
        tool_name: Optional[str] = None,
        environment: Optional[str] = None,
        model_version: Optional[str] = None,
        prompt_version: Optional[str] = None,
    ) -> dict:
        """
        Log an event to the ledger.

        Args:
            agent_id: Identifier for the agent
            action_type: Type of action (e.g., "llm_call", "tool_use")
            input_hash: SHA-256 hash of the input (use hash_content helper)
            output_hash: SHA-256 hash of the output (use hash_content helper)
            tool_name: Optional name of tool used
            environment: Optional environment (e.g., "production", "staging")
            model_version: Optional model version identifier
            prompt_version: Optional prompt version identifier

        Returns:
            dict: The created event record
        """
        payload = {
            "agent_id": agent_id,
            "action_type": action_type,
            "input_hash": input_hash,
            "output_hash": output_hash,
            "tool_name": tool_name,
            "environment": environment,
            "model_version": model_version,
            "prompt_version": prompt_version,
        }
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        response = requests.post(
            f"{self.ledger_url}/events",
            json=payload,
            headers={"X-API-Key": self.api_key, "Content-Type": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def verify_chain(self, agent_id: str) -> dict:
        """
        Verify the hash chain for an agent.

        Args:
            agent_id: Identifier for the agent to verify

        Returns:
            dict: Verification result with is_valid, events_checked, etc.
        """
        response = requests.get(
            f"{self.ledger_url}/verify",
            params={"agent_id": agent_id},
            headers={"X-API-Key": self.api_key},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def list_events(
        self,
        agent_id: Optional[str] = None,
        action_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        """
        List events with optional filters.

        Args:
            agent_id: Filter by agent ID
            action_type: Filter by action type
            page: Page number (default 1)
            page_size: Items per page (default 50)

        Returns:
            dict: List of events with pagination info
        """
        params = {"page": page, "page_size": page_size}
        if agent_id:
            params["agent_id"] = agent_id
        if action_type:
            params["action_type"] = action_type

        response = requests.get(
            f"{self.ledger_url}/events",
            params=params,
            headers={"X-API-Key": self.api_key},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def hash_content(self, content: str) -> str:
        """
        Helper to hash content before logging.

        Args:
            content: The content to hash

        Returns:
            str: SHA-256 hex digest (64 characters)
        """
        return self._hash(content)

    def health(self) -> dict:
        """
        Check ledger health.

        Returns:
            dict: Health status
        """
        response = requests.get(f"{self.ledger_url}/health", timeout=10)
        response.raise_for_status()
        return response.json()
