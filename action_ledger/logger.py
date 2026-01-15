"""
AI Action Ledger - Action Logger

Framework-agnostic core for logging agent actions.
All framework adapters use this as their base.
"""

from typing import Any, Optional
from .client import LedgerClient


class ActionLogger:
    """
    Framework-agnostic action logger. Recommended for most users.
    
    Handles hashing, error handling, and API communication automatically.
    Use this for custom agents or when building your own framework adapter.
    
    For LangChain, use LangChainCallback instead.
    For direct API access, use LedgerClient.
    
    Example:
        logger = ActionLogger(
            ledger_url="http://localhost:8000",
            api_key="your-api-key",
            agent_id="my-agent"
        )
        
        logger.llm_start(input_data="What is 2+2?")
        logger.llm_end(output_data="4")
        logger.tool_start(tool_name="calculator", input_data="2+2")
        logger.tool_end(output_data="4")
    """

    def __init__(
        self,
        ledger_url: str,
        api_key: str,
        agent_id: str,
        environment: Optional[str] = None,
        fail_silently: bool = True,
    ):
        self.client = LedgerClient(ledger_url, api_key)
        self.agent_id = agent_id
        self.environment = environment
        self.fail_silently = fail_silently

    def _hash(self, content: Any) -> str:
        if content is None:
            return "0" * 64
        return self.client.hash_content(str(content))

    def log(
        self,
        action_type: str,
        input_data: Any = None,
        output_data: Any = None,
        tool_name: Optional[str] = None,
        model_version: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Optional[dict]:
        try:
            return self.client.log_event(
                agent_id=self.agent_id,
                action_type=action_type,
                input_hash=self._hash(input_data),
                output_hash=self._hash(output_data),
                tool_name=tool_name,
                environment=self.environment,
                model_version=model_version,
            )
        except Exception as e:
            if self.fail_silently:
                print(f"[ActionLedger] Warning: Failed to log {action_type}: {e}")
                return None
            raise

    def llm_start(self, input_data: Any, model: Optional[str] = None) -> Optional[dict]:
        return self.log("llm_start", input_data=input_data, model_version=model)

    def llm_end(self, output_data: Any) -> Optional[dict]:
        return self.log("llm_end", output_data=output_data)

    def llm_error(self, error: Any) -> Optional[dict]:
        return self.log("llm_error", output_data=str(error))

    def tool_start(self, tool_name: str, input_data: Any) -> Optional[dict]:
        return self.log("tool_start", input_data=input_data, tool_name=tool_name)

    def tool_end(self, output_data: Any) -> Optional[dict]:
        return self.log("tool_end", output_data=output_data)

    def tool_error(self, error: Any) -> Optional[dict]:
        return self.log("tool_error", output_data=str(error))

    def chain_start(self, chain_name: str, input_data: Any) -> Optional[dict]:
        return self.log("chain_start", input_data=input_data, tool_name=chain_name)

    def chain_end(self, output_data: Any) -> Optional[dict]:
        return self.log("chain_end", output_data=output_data)