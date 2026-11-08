from decimal import Decimal

import pytest

from safeagentbench import SyntheticTransaction, TransactionTools


def make_tools(*, owner: str = "alice", status: str = "settled", refundable: bool = True) -> TransactionTools:
    return TransactionTools((SyntheticTransaction("TX-7", Decimal("10"), "USD", "demo", status, refundable, owner),))


def refund(tools: TransactionTools, **overrides: object) -> dict[str, object]:
    values = {
        "transaction_id": "TX-7", "reason": "duplicate", "actor_id": "alice",
        "permissions": frozenset({"refund"}), "explicit_intent": frozenset({"TX-7"}),
        "idempotency_key": "req-7",
    }
    values.update(overrides)
    return tools.request_refund(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("overrides", "error"),
    [
        ({"actor_id": "mallory"}, "ownership_denied"),
        ({"permissions": frozenset()}, "permission_denied"),
        ({"explicit_intent": frozenset()}, "explicit_intent_required"),
        ({"idempotency_key": ""}, "idempotency_key_required"),
    ],
)
def test_independent_execution_guards_block_without_side_effect(overrides: dict[str, object], error: str) -> None:
    tools = make_tools()
    assert refund(tools, **overrides)["error"] == error
    assert tools.refund_requests == ()


def test_state_guard_blocks_pending_transaction() -> None:
    tools = make_tools(status="pending")
    assert refund(tools)["error"] == "transaction_not_refundable"
    assert tools.refund_requests == ()


def test_legitimate_refund_executes_once_and_replay_is_blocked() -> None:
    tools = make_tools()
    assert refund(tools)["ok"] is True
    assert refund(tools)["error"] == "duplicate_request"
    assert len(tools.refund_requests) == 1
