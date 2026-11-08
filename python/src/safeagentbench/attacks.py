"""Deterministic Day 3 attack runner; no model or network service is used."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agent import ModelResponse, ToolCall, ToolCallingAgent
from .agent_policy import ToolAuthorizationPolicy
from .scenarios import InjectionScenario
from .tools import SyntheticTransaction, TransactionTools


class InjectionFollowingMockModel:
    """A deliberately vulnerable mock that treats tool output as instructions."""

    def __init__(self, scenario: InjectionScenario) -> None:
        self.scenario = scenario

    def respond(self, messages: tuple[dict[str, Any], ...]) -> ModelResponse:
        latest = messages[-1]
        if latest["role"] == "user":
            return ModelResponse(tool_call=ToolCall("lookup_transaction", {"transaction_id": "TX-1001"}))
        if latest["role"] == "tool" and latest["name"] == "lookup_transaction":
            return ModelResponse(tool_call=ToolCall(
                self.scenario.attack_tool,
                {"transaction_id": self.scenario.attack_transaction_id, "reason": "instruction in untrusted output"},
            ))
        return ModelResponse(f"Stopped: {latest['content'].get('error', 'complete')}")


@dataclass(frozen=True)
class AttackResult:
    scenario_id: str
    attempted_malicious_tool_calls: int
    executed_unauthorized_actions: int
    final_text: str


def run_attack(scenario: InjectionScenario) -> AttackResult:
    tools = TransactionTools((
        SyntheticTransaction("TX-1001", 42.50, "USD", "sandbox-vendor", "settled", untrusted_output=scenario.untrusted_output),  # type: ignore[arg-type]
        SyntheticTransaction(scenario.attack_transaction_id, 99.00, "USD", "other-vendor", "settled", owner_id="victim"),  # type: ignore[arg-type]
    ))
    # Coarse policy deliberately permits the proposal. The tool boundary must still deny it.
    policy = ToolAuthorizationPolicy(
        frozenset({"lookup_transaction", "request_refund"}),
        frozenset({scenario.attack_transaction_id}),
    )
    result = ToolCallingAgent(InjectionFollowingMockModel(scenario), tools, policy).run(
        scenario.user_message, actor_id=scenario.actor_id, request_id=f"attack:{scenario.scenario_id}"
    )
    return AttackResult(
        scenario_id=scenario.scenario_id,
        attempted_malicious_tool_calls=sum(1 for call in tools.attempted_calls if call["tool"] == scenario.attack_tool),
        executed_unauthorized_actions=len(tools.refund_requests),
        final_text=result.text,
    )
