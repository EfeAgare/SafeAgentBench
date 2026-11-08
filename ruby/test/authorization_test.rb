# frozen_string_literal: true

require_relative "test_helper"

class AuthorizationTest < Minitest::Test
  include SafeAgentBenchTestHelpers

  def test_normalizes_its_delegated_scope
    grant = authorization(allowed_actions: ["PAY", :pay], allowed_currencies: ["usd", "USD"])

    assert_equal [:pay], grant.allowed_actions
    assert_equal ["USD"], grant.allowed_currencies
  end

  def test_approval_threshold_cannot_exceed_limit
    error = assert_raises(ArgumentError) { authorization(human_approval_threshold: "101") }
    assert_match(/cannot exceed/, error.message)
  end
end

