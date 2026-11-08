from safeagentbench import AttackResult, evaluate


def result(identifier: str, attempted: int, executed: int, expected: str, observed: str | None) -> AttackResult:
    return AttackResult(identifier, attempted, executed, "done", "test", expected, observed)


def test_metrics_use_raw_counts_and_explicit_denominators() -> None:
    report = evaluate((
        result("a", 1, 0, "ownership_denied", "ownership_denied"),
        result("b", 1, 1, "permission_denied", None),
    ))
    assert report.total_scenarios == 2
    assert report.attack_attempts == 2
    assert report.unauthorized_executions == 1
    assert report.safe_blocks == 1
    assert report.attack_attempt_rate == 1.0
    assert report.unauthorized_execution_rate == 0.5
    assert report.expected_denial_match_rate == 0.5
    assert report.denial_counts == {"ownership_denied": 1}


def test_empty_evaluation_is_well_defined() -> None:
    report = evaluate(())
    assert report.total_scenarios == 0
    assert report.attack_attempt_rate == 0.0
