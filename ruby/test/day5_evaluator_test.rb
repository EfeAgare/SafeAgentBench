# frozen_string_literal: true

require_relative "test_helper"

class Day5EvaluatorTest < Minitest::Test
  def result(id, attempted, executed, expected, observed)
    SafeAgentBench::AttackResult.new(
      scenario_id: id, attempted_malicious_tool_calls: attempted,
      executed_unauthorized_actions: executed, final_text: "done",
      threat_category: "test", expected_denial: expected, observed_denial: observed
    )
  end

  def test_calculates_counts_and_rates
    report = SafeAgentBench.evaluate([
      result("a", 1, 0, "ownership_denied", "ownership_denied"),
      result("b", 1, 1, "permission_denied", nil)
    ])
    assert_equal 2, report.total_scenarios
    assert_equal 1, report.unauthorized_executions
    assert_equal 0.5, report.unauthorized_execution_rate
    assert_equal({ "ownership_denied" => 1 }, report.denial_counts)
  end
end
