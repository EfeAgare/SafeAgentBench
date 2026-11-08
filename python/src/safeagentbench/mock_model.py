"""Deterministic offline model used for learning and tests."""

import re
from typing import Any

from .agent import ModelResponse, ToolCall


class OfflineMockModel:
    """Imitates tool selection without a network call or API key."""

    def respond(self, messages: tuple[dict[str, Any], ...]) -> ModelResponse:
        latest = messages[-1]
        if latest["role"] == "tool":
            result = latest["content"]
            if not result.get("ok"):
                return ModelResponse(f"I could not complete that request: {result.get('error')}.")
            if latest["name"] == "lookup_transaction":
                return ModelResponse(
                    f"{result['transaction_id']} is {result['status']} for "
                    f"{result['amount']} {result['currency']} at {result['recipient']}."
                )
            return ModelResponse(f"Refund request {result['refund_request_id']} was simulated successfully.")

        prompt = str(messages[0]["content"])
        match = re.search(r"TX-\d+", prompt, re.IGNORECASE)
        if not match:
            return ModelResponse("Please provide a transaction ID such as TX-1001.")
        transaction_id = match.group(0).upper()
        if "refund" in prompt.lower():
            return ModelResponse(tool_call=ToolCall("request_refund", {"transaction_id": transaction_id, "reason": "user requested refund"}))
        return ModelResponse(tool_call=ToolCall("lookup_transaction", {"transaction_id": transaction_id}))

