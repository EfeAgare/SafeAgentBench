# Day 3 — Prompt-injection scenarios

Day 3 introduces safe, synthetic prompt injections embedded in untrusted
transaction/tool output. A deliberately vulnerable offline mock follows the
injected instruction so the benchmark can observe the attempted tool call.

## Python research implementation

- `python/scenarios/day3_prompt_injection.json` — deterministic scenario data
- `python/src/safeagentbench/scenarios.py` — validated scenario loader
- `python/src/safeagentbench/attacks.py` — vulnerable mock and attack runner
- `python/tests/test_day3_attacks.py` — loader and attack integration tests

## Plain Ruby equivalent

- `ruby/scenarios/day3_prompt_injection.json`
- `ruby/lib/safe_agent_bench/scenarios.rb`
- `ruby/lib/safe_agent_bench/attacks.rb`
- `ruby/test/day3_attack_test.rb`

The runner reports attempted malicious calls separately from executed
unauthorized actions. A proposal is evidence of an attempted compromise; only
a simulated state change counts as execution.
