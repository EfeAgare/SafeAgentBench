# frozen_string_literal: true

require_relative "test_helper"

class AuthorizationPolicyTest < Minitest::Test
  include SafeAgentBenchTestHelpers

  def setup
    @authorization = authorization
    @policy = SafeAgentBench::AuthorizationPolicy.new
  end

  def test_allows_a_transaction_within_delegated_scope
    assert @policy.evaluate(transaction, @authorization).allowed?
  end

  def test_denies_each_boundary_violation
    cases = {
      invalid_amount: { amount: "0" },
      action_not_authorized: { action: :refund },
      currency_not_authorized: { currency: "EUR" },
      recipient_not_authorized: { recipient: "attacker" },
      amount_exceeds_limit: { amount: "100.01" },
      approval_required: { amount: "50.01" }
    }

    cases.each do |expected_code, attributes|
      decision = @policy.evaluate(transaction(**attributes), @authorization)
      refute decision.allowed?
      assert_equal expected_code, decision.code
    end
  end

  def test_human_approval_does_not_override_the_hard_limit
    decision = @policy.evaluate(transaction(amount: "101", human_approved: true), @authorization)
    assert_equal :amount_exceeds_limit, decision.code
  end

  def test_rejects_a_replayed_request
    decision = @policy.evaluate(transaction(request_id: "seen"), @authorization, ["seen"])
    assert_equal :duplicate_request, decision.code
  end
end

