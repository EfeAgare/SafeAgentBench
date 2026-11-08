"""Authorization is enforced outside the model and before tool execution."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolDecision:
    allowed: bool
    code: str
    reason: str


class ToolAuthorizationPolicy:
    """Deny-by-default policy for model-proposed tool calls."""

    def __init__(self, allowed_tools: frozenset[str], refund_transaction_ids: frozenset[str] = frozenset()) -> None:
        self.allowed_tools = allowed_tools
        self.refund_transaction_ids = refund_transaction_ids

    def evaluate(self, tool_name: str, arguments: dict[str, Any]) -> ToolDecision:
        if tool_name not in self.allowed_tools:
            return ToolDecision(False, "tool_not_authorized", "tool is outside the delegated scope")
        if tool_name == "request_refund":
            transaction_id = arguments.get("transaction_id")
            if transaction_id not in self.refund_transaction_ids:
                return ToolDecision(False, "refund_not_authorized", "refund requires explicit transaction authorization")
            if not str(arguments.get("reason", "")).strip():
                return ToolDecision(False, "invalid_arguments", "refund reason is required")
        return ToolDecision(True, "allowed", "tool call satisfies authorization policy")

