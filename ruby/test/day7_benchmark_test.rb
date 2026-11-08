# frozen_string_literal: true

require_relative "test_helper"

class Day7BenchmarkTest < Minitest::Test
  def test_report_is_deterministic
    path = File.expand_path("../scenarios/day6_guard_matrix.json", __dir__)
    first = SafeAgentBench.run_benchmark([path])
    second = SafeAgentBench.run_benchmark([path])
    assert_equal first, second
    assert_equal 4, first[:metrics][:total_scenarios]
    assert_equal 0, first[:metrics][:unauthorized_executions]
  end
end
