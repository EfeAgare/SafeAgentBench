# frozen_string_literal: true

require_relative "test_helper"

class Day6ScenarioMatrixTest < Minitest::Test
  def test_each_guard_is_reached
    path = File.expand_path("../scenarios/day6_guard_matrix.json", __dir__)
    results = SafeAgentBench.load_scenarios(path).map { |scenario| SafeAgentBench.run_attack(scenario) }
    assert_equal %w[explicit_intent_required ownership_denied permission_denied transaction_not_refundable], results.map(&:observed_denial).sort
    assert results.all? { |result| result.executed_unauthorized_actions.zero? }
  end
end
