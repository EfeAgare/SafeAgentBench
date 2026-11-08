"""A small, bounded tool-calling agent with structured audit logs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .agent_policy import ToolAuthorizationPolicy
from .tools import TransactionTools


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ModelResponse:
    text: str = ""
    tool_call: ToolCall | None = None


class Model(Protocol):
    def respond(self, messages: tuple[dict[str, Any], ...]) -> ModelResponse: ...


@dataclass(frozen=True)
class AgentResult:
    text: str
    status: str
    steps: int
    logs: tuple[dict[str, Any], ...]


class ToolCallingAgent:
    def __init__(
        self,
        model: Model,
        tools: TransactionTools,
        policy: ToolAuthorizationPolicy,
        max_steps: int = 4,
    ) -> None:
        if max_steps < 1:
            raise ValueError("max_steps must be positive")
        self.model = model
        self.tools = tools
        self.policy = policy
        self.max_steps = max_steps

    def run(
        self,
        user_message: str,
        *,
        actor_id: str = "user-1",
        permissions: frozenset[str] = frozenset({"lookup", "refund"}),
        request_id: str = "agent-request-1",
    ) -> AgentResult:
        messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]
        logs: list[dict[str, Any]] = [{"event": "run_started", "user_message": user_message}]

        for step in range(1, self.max_steps + 1):
            response = self.model.respond(tuple(messages))
            if response.tool_call is None:
                logs.append({"event": "final_response", "step": step, "text": response.text})
                return AgentResult(response.text, "completed", step, tuple(logs))

            call = response.tool_call
            logs.append({"event": "tool_proposed", "step": step, "tool": call.name, "arguments": dict(call.arguments)})
            decision = self.policy.evaluate(call.name, call.arguments)
            logs.append({"event": "policy_decision", "step": step, "tool": call.name, "allowed": decision.allowed, "code": decision.code})

            if decision.allowed:
                tool_result = self._execute(call, user_message, actor_id, permissions, request_id)
            else:
                tool_result = {"ok": False, "error": decision.code, "reason": decision.reason}
            logs.append({"event": "tool_result", "step": step, "tool": call.name, "result": tool_result})
            messages.extend((
                {"role": "assistant", "tool_call": {"name": call.name, "arguments": dict(call.arguments)}},
                {"role": "tool", "name": call.name, "content": tool_result},
            ))

        logs.append({"event": "run_stopped", "reason": "max_steps_exceeded", "max_steps": self.max_steps})
        return AgentResult("I stopped because the tool-call limit was reached.", "max_steps_exceeded", self.max_steps, tuple(logs))

    def _execute(
        self,
        call: ToolCall,
        user_message: str,
        actor_id: str,
        permissions: frozenset[str],
        request_id: str,
    ) -> dict[str, Any]:
        if call.name == "lookup_transaction":
            return self.tools.lookup_transaction(str(call.arguments.get("transaction_id", "")))
        if call.name == "request_refund":
            transaction_id = str(call.arguments.get("transaction_id", "")).upper()
            explicit_intent = (
                frozenset({transaction_id})
                if "refund" in user_message.lower() and transaction_id in user_message.upper()
                else frozenset()
            )
            return self.tools.request_refund(
                transaction_id,
                str(call.arguments.get("reason", "")),
                actor_id=actor_id,
                permissions=permissions,
                explicit_intent=explicit_intent,
                idempotency_key=request_id,
            )
        return {"ok": False, "error": "unknown_tool"}

