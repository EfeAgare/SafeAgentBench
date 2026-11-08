# frozen_string_literal: true

module SafeAgentBench
  def self.run_benchmark(paths)
    scenarios = paths.flat_map { |path| load_scenarios(path) }
    results = scenarios.map { |scenario| run_attack(scenario) }
    {
      schema_version: 1,
      methodology: "offline_deterministic_synthetic",
      metrics: evaluate(results).to_h,
      results: results.map do |result|
        {
          scenario_id: result.scenario_id,
          threat_category: result.threat_category,
          attempted_malicious_tool_calls: result.attempted_malicious_tool_calls,
          executed_unauthorized_actions: result.executed_unauthorized_actions,
          expected_denial: result.expected_denial,
          observed_denial: result.observed_denial
        }
      end
    }
  end
end
