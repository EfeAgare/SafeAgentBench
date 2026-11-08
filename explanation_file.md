# SafeAgentBench Learning Notes

This document explains what each stage of SafeAgentBench adds and how the
pieces work together. The project is completely synthetic: it does not connect
to banks, payment processors, or real customer accounts.

## Day 1: Transaction authorization

Day 1 answers this question:

> Given a structured transaction, should the system allow it?

The application receives a `Transaction` object containing information such as
the action, amount, currency, recipient, and whether a human approved it.

```python
Transaction(
    request_id="req-1",
    action=Action.PAY,
    amount=Decimal("75.00"),
    currency="USD",
    recipient="vendor-a",
)
```

The Day 1 responsibilities are:

- `Transaction` describes the requested payment action.
- `Authorization` describes the actions, currencies, recipients, and amounts
  that have been delegated to the system.
- `AuthorizationPolicy` compares the transaction with that authorization.
- `Decision` contains the result, such as `allowed`, `approval_required`, or
  `amount_exceeds_limit`.
- `PaymentSimulator` records an allowed synthetic payment in its in-memory
  ledger. A denied payment produces no ledger entry.

The policy also rejects invalid amounts, duplicate request IDs, unauthorized
actions, currencies or recipients, and transactions that require missing human
approval.

Day 1 uses normal deterministic application code. There is no AI model making
decisions.

## Day 2: A tool-calling AI agent

Day 2 answers a different question:

> What happens when an AI agent receives a natural-language request and wants
> to use application tools?

For example, the user can write:

```text
Find transaction TX-1001
```

The request follows this path:

```text
User message
    ↓
Offline model interprets the message
    ↓
Model proposes a tool call
    ↓
Independent policy checks the proposal
    ↓
An allowed tool executes
    ↓
The tool result returns to the model
    ↓
The agent produces its final response
```

The important safety rule is:

> The model may propose an action, but the model cannot authorize that action.

Application code independently checks every proposed tool call before it is
executed.

### `agent.py`

`python/src/safeagentbench/agent.py` coordinates the agent workflow. It:

- sends the conversation to the model;
- receives a final answer or proposed tool call;
- sends proposed calls to the authorization policy;
- executes only permitted tools;
- returns tool results to the model;
- records structured audit events; and
- stops after a fixed number of steps.

The step limit prevents a broken or malicious model from requesting tools
forever.

### `mock_model.py`

`python/src/safeagentbench/mock_model.py` is a deterministic offline
replacement for an LLM. It translates simple messages into tool proposals.

For example:

```text
Find transaction TX-1001
```

becomes conceptually:

```python
ToolCall(
    name="lookup_transaction",
    arguments={"transaction_id": "TX-1001"},
)
```

Because it is offline, the project needs no API key, network connection, or
paid model. Its predictable behaviour also makes the agent easy to test.

### `tools.py`

`python/src/safeagentbench/tools.py` contains the operations the model can
propose:

- `lookup_transaction` retrieves a synthetic transaction.
- `request_refund` creates a simulated refund request.

The records live only in memory. A simulated refund never moves money.

### `agent_policy.py`

`python/src/safeagentbench/agent_policy.py` is an independent, deny-by-default
authorization layer. It checks whether the proposed tool is allowed and whether
a refund has been authorized for the specified transaction.

For example:

```text
User: Refund TX-1001
Model: proposes request_refund for TX-1001
Policy: TX-1001 is not authorized for refunds
Result: refund_not_authorized
```

The tool does not execute, and no refund request is stored.

### Structured logs

The agent records dictionaries containing events such as:

```text
run_started
tool_proposed
policy_decision
tool_result
final_response
```

These events make the agent's behaviour inspectable. Tests can confirm what the
model proposed, what the policy decided, whether a tool ran, and why execution
stopped.

## Day 1 compared with Day 2

| Day 1 | Day 2 |
| --- | --- |
| Code creates a structured transaction. | A user sends a natural-language request. |
| A policy evaluates payment details. | A model proposes a tool call. |
| The simulator records allowed payments. | Tools look up transactions or request simulated refunds. |
| Tests payment authorization rules. | Tests whether an agent respects authorization boundaries. |
| No AI or model layer. | Includes an offline mock model. |

Day 1 supplies the fundamental authorization idea. Day 2 places an AI-style
agent in front of tools and demonstrates why the agent must never be its own
authorization authority.

## Python and plain Ruby

Python is the primary research implementation. The `ruby/` directory contains
plain Ruby learning equivalents, without Rails, so the same concepts can be
compared across both languages.

| Python | Plain Ruby | Purpose |
| --- | --- | --- |
| Frozen dataclass | Struct or frozen object | Store a value or response |
| Dictionary | Hash | Store tool arguments and log events |
| Protocol and duck typing | Duck typing | Describe model behaviour |
| `for` loop over a range | `Range#each` | Bound the agent loop |
| pytest | Minitest | Verify behaviour |

## Running the tests

Python:

```bash
cd ~/Desktop/PYTHON/SafeAgentBench/python
source .venv/bin/activate
python -m pytest
```

Plain Ruby:

```bash
cd ~/Desktop/PYTHON/SafeAgentBench/ruby
rake test
```

