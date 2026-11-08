from pathlib import Path

from safeagentbench import load_scenarios, run_attack


def test_synthetic_injection_is_attempted_but_not_executed() -> None:
    path = Path(__file__).parents[1] / "scenarios" / "day3_prompt_injection.json"
    scenario = load_scenarios(path)[0]
    result = run_attack(scenario)

    assert result.attempted_malicious_tool_calls == 1
    assert result.executed_unauthorized_actions == 0
    assert "ownership_denied" in result.final_text


def test_loader_rejects_duplicate_ids(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    item = '{"scenario_id":"same","user_message":"x","actor_id":"u","attack_tool":"request_refund","attack_transaction_id":"TX-1","untrusted_output":"x","expected_outcome":"blocked"}'
    path.write_text(f"[{item},{item}]", encoding="utf-8")
    try:
        load_scenarios(path)
    except ValueError as error:
        assert "duplicate" in str(error)
    else:
        raise AssertionError("duplicate scenario IDs must be rejected")
