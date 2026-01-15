"""
AI Action Ledger - LangChain Callback Handler

Thin adapter that maps LangChain callbacks to ActionLogger.
"""

from typing import Any, Dict, List, Optional
from .logger import ActionLogger

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
    """

    def __init__(
        self,
        ledger_url: str,
        api_key: str,
        agent_id: str,
        environment: Optional[str] = None,
    ):
        super().__init__()
        self.logger = ActionLogger(
            ledger_url=ledger_url,
            api_key=api_key,
            agent_id=agent_id,
            environment=environment,
            fail_silently=True,
        )

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any,
    ) -> None:
        model = serialized.get("name") or serialized.get("kwargs", {}).get("model_name")
        self.logger.llm_start(input_data=prompts, model=model)

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        self.logger.llm_end(output_data=response)

    def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        self.logger.llm_error(error=error)

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        tool_name = serialized.get("name", "unknown")
        self.logger.tool_start(tool_name=tool_name, input_data=input_str)

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        self.logger.tool_end(output_data=output)

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        self.logger.tool_error(error=error)

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        chain_name = serialized.get("name") or serialized.get("id", ["unknown"])[-1]
        self.logger.chain_start(chain_name=chain_name, input_data=inputs)

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        self.logger.chain_end(output_data=outputs)

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        self.logger.log("chain_error", output_data=str(error))