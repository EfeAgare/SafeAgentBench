from decimal import Decimal

from safeagentbench import Action, Authorization, DecisionCode, PaymentSimulator, Transaction


def configured_simulator() -> PaymentSimulator:
    return PaymentSimulator(
        Authorization(
            allowed_actions=frozenset({Action.PAY}),
            allowed_currencies=frozenset({"USD"}),
            allowed_recipients=frozenset({"vendor-a"}),
            per_transaction_limit=Decimal("100.00"),
            human_approval_threshold=Decimal("50.00"),
        )
    )


def test_allowed_payment_is_recorded_in_memory() -> None:
    simulator = configured_simulator()
    request = Transaction("req-1", Action.PAY, Decimal("20.00"), "usd", "vendor-a")

    assert simulator.submit(request).code is DecisionCode.ALLOWED
    assert len(simulator.ledger) == 1
    assert simulator.total_paid("USD") == Decimal("20.00")


def test_denied_payment_has_no_ledger_side_effect() -> None:
    simulator = configured_simulator()
    request = Transaction("req-1", Action.PAY, Decimal("20.00"), "USD", "unknown")

    assert simulator.submit(request).code is DecisionCode.RECIPIENT_NOT_AUTHORIZED
    assert simulator.ledger == ()


def test_successful_request_cannot_be_replayed() -> None:
    simulator = configured_simulator()
    request = Transaction("req-1", Action.PAY, Decimal("20.00"), "USD", "vendor-a")

    assert simulator.submit(request).allowed is True
    assert simulator.submit(request).code is DecisionCode.DUPLICATE_REQUEST
    assert len(simulator.ledger) == 1

