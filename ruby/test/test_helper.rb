# frozen_string_literal: true

$LOAD_PATH.unshift File.expand_path("../lib", __dir__)

require "minitest/autorun"
require "safe_agent_bench"

module SafeAgentBenchTestHelpers
  def authorization(**overrides)
    defaults = {
      allowed_actions: [:pay],
      allowed_currencies: ["USD"],
      allowed_recipients: ["vendor-a"],
      per_transaction_limit: "100.00",
      human_approval_threshold: "50.00"
    }
    SafeAgentBench::Authorization.new(**defaults.merge(overrides))
  end

  def transaction(**overrides)
    defaults = {
      request_id: "req-1", action: :pay, amount: "25.00",
      currency: "USD", recipient: "vendor-a", human_approved: false
    }
    SafeAgentBench::Transaction.new(**defaults.merge(overrides))
  end
end

