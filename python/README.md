# SafeAgentBench — Day 1

SafeAgentBench is a small empirical safety benchmark for AI agents that can propose payment actions. Day 1 asks one concrete question:

> Does the agent-facing execution layer enforce the user's authorization boundaries even when a proposed action is unsafe?

This repository contains a deterministic authorization policy, a synthetic in-memory payment simulator, and pytest experiments covering common boundary violations. It has **no network calls, API keys, bank connections, payment processors, or real financial integrations**.

## What the benchmark tests

- Deny-by-default action scope (`pay` versus `refund`)
- Currency and recipient allowlists
- Per-transaction spending limits
- Explicit human approval above a threshold
- Replay protection through unique request IDs
- No ledger mutation after a denied action
- Machine-readable decision codes for later analysis

The policy is intentionally separate from the simulator. `AuthorizationPolicy.evaluate` is pure and auditable; `PaymentSimulator.submit` is the synthetic side-effect boundary.

## Setup

Requires Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
safeagentbench
```

Expected CLI behavior: one request is allowed, one requires human approval, one has an unauthorized recipient, and only the allowed request appears in the in-memory ledger.

If you prefer not to activate the environment, run `.venv/bin/pytest` and `.venv/bin/safeagentbench` directly.

## Map from plain Ruby to Python

| Ruby concept | Python equivalent |
|---|---|
| immutable plain objects | frozen `@dataclass` objects in `models.py` |
| policy object | `AuthorizationPolicy` |
| in-memory simulator | `PaymentSimulator` and its in-memory ledger |
| symbols / enums | `str, Enum` decision codes and actions |
| `BigDecimal` | `decimal.Decimal` (never floats for amounts) |
| table-driven Minitest assertions | parametrized pytest cases |
| `ruby ...` / `rake test` | `pytest` |

The tests read much like RSpec: fixtures provide setup, plain `test_*` functions are examples, and `@pytest.mark.parametrize` expresses a table of adversarial cases.

## Repository layout

```text
src/safeagentbench/
  models.py       # requests, authorization grants, and decisions
  policy.py       # pure deny-by-default evaluator
  simulator.py    # synthetic in-memory execution boundary
  cli.py          # three-case demonstration
tests/
  test_authorization_policy.py
  test_payment_simulator.py
```

## Safety claims and non-claims

Day 1 demonstrates that explicit constraints can be encoded and tested at an execution boundary. It does **not** demonstrate that an LLM reliably understands user intent, resists prompt injection, or chooses safe actions. No LLM is used yet, so the policy layer—not model behavior—is the experimental subject.

This distinction matters for a research portfolio: each later claim should be tied to a measurable experiment rather than a product feature.

## Next steps for the residency portfolio

Keep the next iterations empirical and small:

1. **Day 2 — scenario dataset:** represent benign and adversarial requests as versioned JSONL, including expected decision codes and threat labels.
2. **Day 3 — evaluation runner:** report pass rate by threat category, false-allow rate, false-deny rate, and deterministic seeds.
3. **Day 4 — agent proposal layer:** let a model propose a typed `Transaction`, but never bypass the policy. Store model, prompt version, and raw proposal for reproducibility.
4. **Day 5 — adversarial evaluation:** test prompt injection, ambiguous delegation, recipient substitution, amount manipulation, and replay attacks.
5. **Write-up:** state hypotheses before results, publish failures, compare at least one baseline, and document limitations.

Avoid real payment integrations during this phase. The compelling Anthropic Residency signal is careful experimental design around agentic risk: explicit threat models, reproducible evaluations, interpretable failures, and honest claims.

