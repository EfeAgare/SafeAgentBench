"""Load safe, synthetic prompt-injection benchmark scenarios."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class InjectionScenario:
    scenario_id: str
    user_message: str
    actor_id: str
    attack_tool: str
    attack_transaction_id: str
    untrusted_output: str
    expected_outcome: str


def load_scenarios(path: str | Path) -> tuple[InjectionScenario, ...]:
    data: Any = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("scenario file must contain a JSON list")
    scenarios: list[InjectionScenario] = []
    seen: set[str] = set()
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("each scenario must be an object")
        scenario = InjectionScenario(**item)
        if scenario.scenario_id in seen:
            raise ValueError(f"duplicate scenario_id: {scenario.scenario_id}")
        if scenario.attack_tool not in {"request_refund", "lookup_transaction"}:
            raise ValueError("scenarios may only use synthetic benchmark tools")
        seen.add(scenario.scenario_id)
        scenarios.append(scenario)
    return tuple(scenarios)
