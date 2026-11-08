# frozen_string_literal: true

require "json"

module SafeAgentBench
  InjectionScenario = Struct.new(
    :scenario_id, :user_message, :actor_id, :attack_tool,
    :attack_transaction_id, :untrusted_output, :expected_outcome,
    :threat_category, :attack_owner_id, :actor_permissions,
    :attack_status, :attack_refundable, :expected_denial,
    keyword_init: true
  )

  def self.load_scenarios(path)
    seen = []
    JSON.parse(File.read(path), symbolize_names: true).map do |item|
      raise ArgumentError, "duplicate scenario_id: #{item[:scenario_id]}" if seen.include?(item[:scenario_id])
      raise ArgumentError, "unsupported synthetic tool" unless %w[request_refund lookup_transaction].include?(item[:attack_tool])

      seen << item[:scenario_id]
      defaults = {
        threat_category: "prompt_injection", attack_owner_id: "victim",
        actor_permissions: %w[lookup refund], attack_status: "settled",
        attack_refundable: true, expected_denial: "ownership_denied"
      }
      InjectionScenario.new(**defaults.merge(item))
    end.freeze
  end
end
