"""In-memory payment simulator. It never contacts a financial service."""

from dataclasses import dataclass
from decimal import Decimal

from .models import Authorization, Decision, DecisionCode, Transaction
from .policy import AuthorizationPolicy


@dataclass(frozen=True)
class LedgerEntry:
    request_id: str
    recipient: str
    amount: Decimal
    currency: str


class PaymentSimulator:
    """Apply allowed synthetic payments to an in-memory ledger."""

    def __init__(self, authorization: Authorization, policy: AuthorizationPolicy | None = None) -> None:
        self.authorization = authorization
        self.policy = policy or AuthorizationPolicy()
        self._ledger: list[LedgerEntry] = []

    @property
    def ledger(self) -> tuple[LedgerEntry, ...]:
        return tuple(self._ledger)

    def submit(self, transaction: Transaction) -> Decision:
        seen = frozenset(entry.request_id for entry in self._ledger)
        decision = self.policy.evaluate(transaction, self.authorization, seen)
        if decision.allowed:
            self._ledger.append(
                LedgerEntry(
                    request_id=transaction.request_id,
                    recipient=transaction.recipient,
                    amount=transaction.amount,
                    currency=transaction.currency.upper(),
                )
            )
        return decision

    def total_paid(self, currency: str) -> Decimal:
        normalized = currency.upper()
        return sum(
            (entry.amount for entry in self._ledger if entry.currency == normalized),
            start=Decimal("0"),
        )

