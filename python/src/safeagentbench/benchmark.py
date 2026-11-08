"""Day 7 reproducible offline benchmark runner and JSON report writer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .attacks import run_attack
from .evaluator import evaluate
from .scenarios import load_scenarios


def run_benchmark(paths: tuple[str | Path, ...]) -> dict[str, object]:
    scenarios = tuple(scenario for path in paths for scenario in load_scenarios(path))
    results = tuple(run_attack(scenario) for scenario in scenarios)
    return {
        "schema_version": 1,
        "methodology": "offline_deterministic_synthetic",
        "metrics": evaluate(results).to_dict(),
        "results": [
            {
                "scenario_id": result.scenario_id,
                "threat_category": result.threat_category,
                "attempted_malicious_tool_calls": result.attempted_malicious_tool_calls,
                "executed_unauthorized_actions": result.executed_unauthorized_actions,
                "expected_denial": result.expected_denial,
                "observed_denial": result.observed_denial,
            }
            for result in results
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SafeAgentBench offline scenarios")
    parser.add_argument("scenario_files", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_benchmark(tuple(args.scenario_files))
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
