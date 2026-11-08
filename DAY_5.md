# Day 5 — Evaluation metrics

Day 5 turns recorded outcomes into transparent measurements. The evaluator
reports raw scenario counts alongside attack-attempt, unauthorized-execution,
safe-block, and expected-denial-match rates. It also groups denials by code and
retains every scenario ID.

Python is canonical in `python/src/safeagentbench/evaluator.py`, tested by
`python/tests/test_day5_evaluator.py`. The plain Ruby learning equivalent is in
`ruby/lib/safe_agent_bench/evaluator.rb` with its matching Minitest file.

These are measurements of deterministic synthetic fixtures—not claims about a
production model or real payment system.
