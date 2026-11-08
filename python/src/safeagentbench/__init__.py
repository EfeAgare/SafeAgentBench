"""SafeAgentBench: synthetic authorization tests for payment-capable agents."""

from .models import Action, Authorization, Decision, DecisionCode, Transaction
from .policy import AuthorizationPolicy
from .simulator import PaymentSimulator
from .agent import AgentResult, ModelResponse, ToolCall, ToolCallingAgent
from .agent_policy import ToolAuthorizationPolicy, ToolDecision
from .mock_model import OfflineMockModel
from .tools import SyntheticTransaction, TransactionTools
from .attacks import AttackResult, InjectionFollowingMockModel, run_attack
from .scenarios import InjectionScenario, load_scenarios

__all__ = [
    "Action",
    "Authorization",
    "AuthorizationPolicy",
    "Decision",
    "DecisionCode",
    "PaymentSimulator",
    "Transaction",
    "AgentResult",
    "ModelResponse",
    "OfflineMockModel",
    "SyntheticTransaction",
    "ToolAuthorizationPolicy",
    "ToolCall",
    "ToolCallingAgent",
    "ToolDecision",
    "TransactionTools",
    "AttackResult",
    "InjectionFollowingMockModel",
    "InjectionScenario",
    "load_scenarios",
    "run_attack",
]

