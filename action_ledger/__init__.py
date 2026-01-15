"""
AI Action Ledger SDK

Tamper-evident audit logging for AI agent actions.
"""

__version__ = "0.1.0"

from .client import LedgerClient
from .logger import ActionLogger

# LangChain callback is optional (requires langchain)
try:
    from .langchain_callback import ActionLedgerCallback
except ImportError:
    ActionLedgerCallback = None

__all__ = ["LedgerClient", "ActionLogger", "ActionLedgerCallback", "__version__"]