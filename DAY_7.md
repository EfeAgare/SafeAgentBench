# Day 7 — Reproducible benchmark reporting

Day 7 composes scenario loading, attack execution, and evaluation into a single
offline benchmark workflow. The report has a schema version, methodology label,
aggregate metrics, and per-scenario outcomes. It intentionally omits timestamps
so the same fixtures produce byte-for-byte stable JSON.

Run Python:

```bash
cd python
python -m safeagentbench.benchmark scenarios/day3_prompt_injection.json scenarios/day6_guard_matrix.json
```

Write a report when desired:

```bash
python -m safeagentbench.benchmark scenarios/day6_guard_matrix.json --output results.json
```

The report describes only the executed deterministic mocks. It must not be
presented as empirical evidence about live language models.
