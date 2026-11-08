"""Deterministic Day 3 attack runner; no model or network service is used."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
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
    threat_category: str
    expected_denial: str
    observed_denial: str | None


def run_attack(scenario: InjectionScenario) -> AttackResult:
    tools = TransactionTools((
        SyntheticTransaction("TX-1001", Decimal("42.50"), "USD", "sandbox-vendor", "settled", untrusted_output=scenario.untrusted_output),
        SyntheticTransaction(
            scenario.attack_transaction_id,
            Decimal("99.00"),
            "USD",
            "other-vendor",
            scenario.attack_status,
            scenario.attack_refundable,
            scenario.attack_owner_id,
        ),
    ))
    # Coarse policy deliberately permits the proposal. The tool boundary must still deny it.
    policy = ToolAuthorizationPolicy(
        frozenset({"lookup_transaction", "request_refund"}),
        frozenset({scenario.attack_transaction_id}),
    )
    result = ToolCallingAgent(InjectionFollowingMockModel(scenario), tools, policy).run(
        scenario.user_message,
        actor_id=scenario.actor_id,
        permissions=frozenset(scenario.actor_permissions),
        request_id=f"attack:{scenario.scenario_id}",
    )
    denied_results = [
        entry["result"] for entry in result.logs
        if entry["event"] == "tool_result" and entry["tool"] == scenario.attack_tool and not entry["result"].get("ok")
    ]
    return AttackResult(
        scenario_id=scenario.scenario_id,
        attempted_malicious_tool_calls=sum(1 for call in tools.attempted_calls if call["tool"] == scenario.attack_tool),
        executed_unauthorized_actions=len(tools.refund_requests),
        final_text=result.text,
        threat_category=scenario.threat_category,
        expected_denial=scenario.expected_denial,
        observed_denial=denied_results[-1].get("error") if denied_results else None,
    )
