import json
from pathlib import Path

from safeagentbench import run_benchmark


def test_benchmark_report_is_deterministic_and_machine_readable() -> None:
    path = Path(__file__).parents[1] / "scenarios" / "day6_guard_matrix.json"
    first = run_benchmark((path,))
    second = run_benchmark((path,))
    assert first == second
    assert first["schema_version"] == 1
    assert first["metrics"]["total_scenarios"] == 4  # type: ignore[index]
    assert first["metrics"]["unauthorized_executions"] == 0  # type: ignore[index]
    json.dumps(first)
