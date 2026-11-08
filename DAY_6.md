# Day 6 — Adversarial scenario matrix

Day 6 expands the fixture set so different scenarios independently exercise
ownership, actor permission, explicit user intent, and transaction-state
boundaries. Each fixture declares its threat category and expected denial code.

- Python: `python/scenarios/day6_guard_matrix.json`
- Plain Ruby: `ruby/scenarios/day6_guard_matrix.json`
- Tests: `test_day6_scenario_matrix.py` and `day6_scenario_matrix_test.rb`

All data remains synthetic, obvious, offline, and safe. The matrix improves
coverage; it does not establish general prompt-injection resistance.
