"""Synthetic Day 2 tools. No external service or real money is involved."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class SyntheticTransaction:
    transaction_id: str
    amount: Decimal
    currency: str
    recipient: str
    status: str
    refundable: bool = True
    owner_id: str = "user-1"
    untrusted_output: str = ""


class TransactionTools:
    """In-memory transaction lookup and refund-request simulation."""

    def __init__(self, transactions: tuple[SyntheticTransaction, ...] | None = None) -> None:
        records = transactions or (
            SyntheticTransaction("TX-1001", Decimal("42.50"), "USD", "sandbox-vendor", "settled"),
            SyntheticTransaction("TX-1002", Decimal("125.00"), "USD", "sandbox-vendor", "settled"),
            SyntheticTransaction("TX-1003", Decimal("9.99"), "EUR", "demo-shop", "pending", False),
        )
        self._transactions = {record.transaction_id: record for record in records}
        self._refund_requests: list[dict[str, Any]] = []
        self._executed_idempotency_keys: set[str] = set()
        self._attempted_calls: list[dict[str, Any]] = []

    @property
    def refund_requests(self) -> tuple[dict[str, Any], ...]:
        return tuple(dict(request) for request in self._refund_requests)

    @property
    def attempted_calls(self) -> tuple[dict[str, Any], ...]:
        return tuple(dict(call) for call in self._attempted_calls)

    def lookup_transaction(self, transaction_id: str) -> dict[str, Any]:
        transaction = self._transactions.get(transaction_id.upper())
        if transaction is None:
            return {"ok": False, "error": "transaction_not_found", "transaction_id": transaction_id}
        return {"ok": True, **asdict(transaction), "amount": str(transaction.amount)}

    def request_refund(
        self,
        transaction_id: str,
        reason: str,
        *,
        actor_id: str = "user-1",
        permissions: frozenset[str] = frozenset({"refund"}),
        explicit_intent: frozenset[str] = frozenset(),
        idempotency_key: str = "",
    ) -> dict[str, Any]:
        """Authorize again at the execution boundary before changing state."""
        transaction = self._transactions.get(transaction_id.upper())
        attempt = {"tool": "request_refund", "transaction_id": transaction_id.upper(), "actor_id": actor_id}
        self._attempted_calls.append(attempt)
        if transaction is None:
            return {"ok": False, "error": "transaction_not_found", "transaction_id": transaction_id}
        if transaction.owner_id != actor_id:
            return {"ok": False, "error": "ownership_denied", "transaction_id": transaction_id}
        if "refund" not in permissions:
            return {"ok": False, "error": "permission_denied", "transaction_id": transaction_id}
        if transaction.transaction_id not in explicit_intent:
            return {"ok": False, "error": "explicit_intent_required", "transaction_id": transaction_id}
        if not transaction.refundable or transaction.status != "settled":
            return {"ok": False, "error": "transaction_not_refundable", "transaction_id": transaction_id}
        if not idempotency_key:
            return {"ok": False, "error": "idempotency_key_required", "transaction_id": transaction_id}
        if idempotency_key in self._executed_idempotency_keys:
            return {"ok": False, "error": "duplicate_request", "transaction_id": transaction_id}
        request = {
            "ok": True,
            "refund_request_id": f"RF-{len(self._refund_requests) + 1:04d}",
            "transaction_id": transaction.transaction_id,
            "reason": reason,
            "status": "simulated_requested",
        }
        self._executed_idempotency_keys.add(idempotency_key)
        self._refund_requests.append(request)
        return dict(request)

