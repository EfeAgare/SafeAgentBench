"""A deny-by-default, auditable authorization policy."""

from .models import Authorization, Decision, DecisionCode, Transaction


class AuthorizationPolicy:
    """Evaluate requests without causing side effects.

    Checks are deliberately ordered. A benchmark can therefore assert both the
    final outcome and the first boundary that stopped an unsafe request.
    """

    def evaluate(
        self,
        transaction: Transaction,
        authorization: Authorization,
        seen_request_ids: frozenset[str] = frozenset(),
    ) -> Decision:
        if transaction.amount <= 0:
            return self._deny(DecisionCode.INVALID_AMOUNT, "amount must be positive")
        if transaction.request_id in seen_request_ids:
            return self._deny(DecisionCode.DUPLICATE_REQUEST, "request_id was already processed")
        if transaction.action not in authorization.allowed_actions:
            return self._deny(DecisionCode.ACTION_NOT_AUTHORIZED, "action is outside the delegated scope")
        if transaction.currency.upper() not in authorization.allowed_currencies:
            return self._deny(DecisionCode.CURRENCY_NOT_AUTHORIZED, "currency is outside the delegated scope")
        if transaction.recipient not in authorization.allowed_recipients:
            return self._deny(DecisionCode.RECIPIENT_NOT_AUTHORIZED, "recipient is not on the allowlist")
        if transaction.amount > authorization.per_transaction_limit:
            return self._deny(DecisionCode.AMOUNT_EXCEEDS_LIMIT, "amount exceeds the per-transaction limit")
        if (
            transaction.amount > authorization.human_approval_threshold
            and not transaction.human_approved
        ):
            return self._deny(DecisionCode.APPROVAL_REQUIRED, "amount requires explicit human approval")
        return Decision(True, DecisionCode.ALLOWED, "request satisfies every authorization constraint")

    @staticmethod
    def _deny(code: DecisionCode, reason: str) -> Decision:
        return Decision(False, code, reason)

