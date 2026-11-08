"""Typed values used by the policy and the synthetic simulator."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class Action(str, Enum):
    PAY = "pay"
    REFUND = "refund"


class DecisionCode(str, Enum):
    ALLOWED = "allowed"
    ACTION_NOT_AUTHORIZED = "action_not_authorized"
    CURRENCY_NOT_AUTHORIZED = "currency_not_authorized"
    RECIPIENT_NOT_AUTHORIZED = "recipient_not_authorized"
    AMOUNT_EXCEEDS_LIMIT = "amount_exceeds_limit"
    APPROVAL_REQUIRED = "approval_required"
    DUPLICATE_REQUEST = "duplicate_request"
    INVALID_AMOUNT = "invalid_amount"


@dataclass(frozen=True)
class Transaction:
    request_id: str
    action: Action
    amount: Decimal
    currency: str
    recipient: str
    human_approved: bool = False


@dataclass(frozen=True)
class Authorization:
    allowed_actions: frozenset[Action]
    allowed_currencies: frozenset[str]
    allowed_recipients: frozenset[str]
    per_transaction_limit: Decimal
    human_approval_threshold: Decimal


@dataclass(frozen=True)
class Decision:
    allowed: bool
    code: DecisionCode
    reason: str

