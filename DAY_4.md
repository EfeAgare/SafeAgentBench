# Day 4 — Execution-boundary authorization

Day 4 treats model output as an untrusted proposal. The refund tool independently
checks authorization immediately before it can change simulated state.

## Required guards

1. The actor owns the transaction.
2. The actor has refund permission.
3. The user's explicit intent names the exact transaction.
4. The transaction is settled and refundable.
5. The idempotency key has not already executed.

## Python research implementation

- `python/src/safeagentbench/tools.py` — independent execution checks and state
- `python/src/safeagentbench/agent.py` — passes actor, intent, and request context
- `python/tests/test_day4_execution_guards.py` — unit tests for every guard
- `python/tests/test_agent.py` — allowed and denied agent integration behavior

## Plain Ruby equivalent

- `ruby/lib/safe_agent_bench/agent.rb` — tool boundary and agent context
- `ruby/test/day4_execution_guard_test.rb` — guard and replay tests
- `ruby/test/agent_test.rb` — integration behavior

The prompt-level tool policy remains useful as an early filter, but it is not
the authority. A denied execution-boundary check creates no refund record.
