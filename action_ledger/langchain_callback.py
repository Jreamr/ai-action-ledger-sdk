"""
AI Action Ledger - LangChain Callback Handler

Automatically logs LangChain events to AI Action Ledger.
"""

from typing import Any, Dict, List, Optional
from .client import LedgerClient

try:
    from langchain.callbacks.base import BaseCallbackHandler
except ImportError:
    raise ImportError(
        "langchain is required for ActionLedgerCallback. "
        "Install with: pip install action-ledger[langchain]"
    )


class ActionLedgerCallback(BaseCallbackHandler):
    """
    LangChain callback handler that logs actions to AI Action Ledger.

    Usage:
        from action_ledger import ActionLedgerCallback

        callback = ActionLedgerCallback(
            ledger_url="http://localhost:8000",
            api_key="your-api-key",
            agent_id="my-agent"
        )

        llm = OpenAI(callbacks=[callback])
        llm.invoke("Hello!")  # Automatically logged
    """

    def __init__(
        self,
        ledger_url: str,
        api_key: str,
        agent_id: str,
        environment: Optional[str] = None,
    ):
        """
        Initialize the callback handler.

        Args:
            ledger_url: Base URL of the ledger API
            api_key: API key for authentication
            agent_id: Identifier for this agent
            environment: Optional environment tag
        """
        super().__init__()
        self.client = LedgerClient(ledger_url, api_key)
        self.agent_id = agent_id
        self.environment = environment

    def _hash(self, content: Any) -> str:
        """Hash any content."""
        return self.client.hash_content(str(content))

    def _safe_log(self, **kwargs) -> None:
        """Log event, catching errors to avoid breaking the chain."""
        try:
            self.client.log_event(**kwargs)
        except Exception as e:
            # Don't break the LangChain execution if logging fails
            print(f"[ActionLedger] Warning: Failed to log event: {e}")

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any,
    ) -> None:
        """Log when LLM starts."""
        self._safe_log(
            agent_id=self.agent_id,
            action_type="llm_start",
            tool_name=serialized.get("name", "unknown"),
            input_hash=self._hash(prompts),
            output_hash="0" * 64,
            environment=self.environment,
        )

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """Log when LLM completes."""
        self._safe_log(
            agent_id=self.agent_id,
            action_type="llm_end",
            input_hash="0" * 64,
            output_hash=self._hash(response),
            environment=self.environment,
        )

    def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        """Log when LLM errors."""
        self._safe_log(
            agent_id=self.agent_id,
            action_type="llm_error",
            input_hash="0" * 64,
            output_hash=self._hash(str(error)),
            environment=self.environment,
        )

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        """Log when a tool is called."""
        self._safe_log(
            agent_id=self.agent_id,
            action_type="tool_start",
            tool_name=serialized.get("name"),
            input_hash=self._hash(input_str),
            output_hash="0" * 64,
            environment=self.environment,
        )

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Log when a tool completes."""
        self._safe_log(
            agent_id=self.agent_id,
            action_type="tool_end",
            input_hash="0" * 64,
            output_hash=self._hash(output),
            environment=self.environment,
        )

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        """Log when a tool errors."""
        self._safe_log(
            agent_id=self.agent_id,
            action_type="tool_error",
            input_hash="0" * 64,
            output_hash=self._hash(str(error)),
            environment=self.environment,
        )

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """Log when a chain starts."""
        self._safe_log(
            agent_id=self.agent_id,
            action_type="chain_start",
            tool_name=serialized.get("name", "unknown"),
            input_hash=self._hash(inputs),
            output_hash="0" * 64,
            environment=self.environment,
        )

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Log when a chain completes."""
        self._safe_log(
            agent_id=self.agent_id,
            action_type="chain_end",
            input_hash="0" * 64,
            output_hash=self._hash(outputs),
            environment=self.environment,
        )

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        """Log when a chain errors."""
        self._safe_log(
            agent_id=self.agent_id,
            action_type="chain_error",
            input_hash="0" * 64,
            output_hash=self._hash(str(error)),
            environment=self.environment,
        )
