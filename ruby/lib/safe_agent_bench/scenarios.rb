# frozen_string_literal: true

require "json"

module SafeAgentBench
  InjectionScenario = Struct.new(
    :scenario_id, :user_message, :actor_id, :attack_tool,
    :attack_transaction_id, :untrusted_output, :expected_outcome,
    keyword_init: true
  )

  def self.load_scenarios(path)
    seen = []
    JSON.parse(File.read(path), symbolize_names: true).map do |item|
      raise ArgumentError, "duplicate scenario_id: #{item[:scenario_id]}" if seen.include?(item[:scenario_id])
      raise ArgumentError, "unsupported synthetic tool" unless %w[request_refund lookup_transaction].include?(item[:attack_tool])

      seen << item[:scenario_id]
      InjectionScenario.new(**item)
    end.freeze
  end
end
