"""
AI Action Ledger - LlamaIndex Callback Handler

INTERNAL / EXPERIMENTAL - Not documented or announced.
"""

from typing import Any, Dict, Optional
from .logger import ActionLogger

try:
    from llama_index.core.callbacks.base import BaseCallbackHandler
    from llama_index.core.callbacks import CBEventType
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    LLAMAINDEX_AVAILABLE = False
    BaseCallbackHandler = object
    CBEventType = None


class LlamaIndexCallback(BaseCallbackHandler if LLAMAINDEX_AVAILABLE else object):
    """
    LlamaIndex callback handler. EXPERIMENTAL - Not officially supported.
    """

    def __init__(
        self,
        ledger_url: str,
        api_key: str,
        agent_id: str,
        environment: Optional[str] = None,
    ):
        if not LLAMAINDEX_AVAILABLE:
            raise ImportError(
                "llama-index is required for LlamaIndexCallback. "
                "Install with: pip install llama-index"
            )
        
        super().__init__(event_starts_to_ignore=[], event_ends_to_ignore=[])
        
        self.logger = ActionLogger(
            ledger_url=ledger_url,
            api_key=api_key,
            agent_id=agent_id,
            environment=environment,
            fail_silently=True,
        )

    def on_event_start(
        self,
        event_type: "CBEventType",
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        parent_id: str = "",
        **kwargs: Any,
    ) -> str:
        payload = payload or {}
        
        if event_type == CBEventType.LLM:
            self.logger.llm_start(
                input_data=payload.get("messages") or payload.get("prompt"),
                model=payload.get("model_name"),
            )
        elif event_type == CBEventType.FUNCTION_CALL:
            self.logger.tool_start(
                tool_name=payload.get("tool_name", "unknown"),
                input_data=payload.get("arguments"),
            )
        elif event_type == CBEventType.QUERY:
            self.logger.chain_start(
                chain_name="query",
                input_data=payload.get("query_str"),
            )
        
        return event_id

    def on_event_end(
        self,
        event_type: "CBEventType",
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        payload = payload or {}
        
        if event_type == CBEventType.LLM:
            self.logger.llm_end(output_data=payload.get("response"))
        elif event_type == CBEventType.FUNCTION_CALL:
            self.logger.tool_end(output_data=payload.get("function_output"))
        elif event_type == CBEventType.QUERY:
            self.logger.chain_end(output_data=payload.get("response"))

    def start_trace(self, trace_id: Optional[str] = None) -> None:
        pass

    def end_trace(
        self,
        trace_id: Optional[str] = None,
        trace_map: Optional[Dict[str, Any]] = None,
    ) -> None:
        pass