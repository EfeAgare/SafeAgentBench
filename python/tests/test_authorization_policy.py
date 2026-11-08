from decimal import Decimal

import pytest

from safeagentbench import Action, Authorization, AuthorizationPolicy, DecisionCode, Transaction


@pytest.fixture
def authorization() -> Authorization:
    return Authorization(
        allowed_actions=frozenset({Action.PAY}),
        allowed_currencies=frozenset({"USD"}),
        allowed_recipients=frozenset({"vendor-a"}),
        per_transaction_limit=Decimal("100.00"),
        human_approval_threshold=Decimal("50.00"),
    )


def transaction(**overrides: object) -> Transaction:
    values = {
        "request_id": "req-1",
        "action": Action.PAY,
        "amount": Decimal("25.00"),
        "currency": "USD",
        "recipient": "vendor-a",
        "human_approved": False,
    }
    values.update(overrides)
    return Transaction(**values)  # type: ignore[arg-type]


def test_allows_request_within_delegated_scope(authorization: Authorization) -> None:
    decision = AuthorizationPolicy().evaluate(transaction(), authorization)
    assert decision.allowed is True
    assert decision.code is DecisionCode.ALLOWED


@pytest.mark.parametrize(
    ("overrides", "expected_code"),
    [
        ({"amount": Decimal("0")}, DecisionCode.INVALID_AMOUNT),
        ({"action": Action.REFUND}, DecisionCode.ACTION_NOT_AUTHORIZED),
        ({"currency": "EUR"}, DecisionCode.CURRENCY_NOT_AUTHORIZED),
        ({"recipient": "attacker"}, DecisionCode.RECIPIENT_NOT_AUTHORIZED),
        ({"amount": Decimal("100.01")}, DecisionCode.AMOUNT_EXCEEDS_LIMIT),
        ({"amount": Decimal("50.01")}, DecisionCode.APPROVAL_REQUIRED),
    ],
)
def test_denies_boundary_violations(
    authorization: Authorization,
    overrides: dict[str, object],
    expected_code: DecisionCode,
) -> None:
    decision = AuthorizationPolicy().evaluate(transaction(**overrides), authorization)
    assert decision.allowed is False
    assert decision.code is expected_code


def test_human_approval_unlocks_only_the_approval_boundary(authorization: Authorization) -> None:
    approved = transaction(amount=Decimal("75.00"), human_approved=True)
    assert AuthorizationPolicy().evaluate(approved, authorization).allowed is True

    over_limit = transaction(amount=Decimal("101.00"), human_approved=True)
    assert AuthorizationPolicy().evaluate(over_limit, authorization).code is DecisionCode.AMOUNT_EXCEEDS_LIMIT


def test_rejects_replayed_request(authorization: Authorization) -> None:
    decision = AuthorizationPolicy().evaluate(
        transaction(request_id="already-seen"),
        authorization,
        frozenset({"already-seen"}),
    )
    assert decision.code is DecisionCode.DUPLICATE_REQUEST

