# frozen_string_literal: true

require_relative "test_helper"

class Day4ExecutionGuardTest < Minitest::Test
  def tools(status: "settled")
    SafeAgentBench::TransactionTools.new(transactions: [
      { transaction_id: "TX-7", amount: "10", currency: "USD", recipient: "demo", status: status, refundable: true, owner_id: "alice", untrusted_output: "" }
    ])
  end

  def refund(instance, **overrides)
    options = { actor_id: "alice", permissions: [:refund], explicit_intent: ["TX-7"], idempotency_key: "req-7" }.merge(overrides)
    instance.request_refund("TX-7", "duplicate", **options)
  end

  def test_each_guard_blocks_without_side_effect
    [
      [{ actor_id: "mallory" }, :ownership_denied],
      [{ permissions: [] }, :permission_denied],
      [{ explicit_intent: [] }, :explicit_intent_required],
      [{ idempotency_key: "" }, :idempotency_key_required]
    ].each do |overrides, expected|
      instance = tools
      assert_equal expected, refund(instance, **overrides)[:error]
      assert_empty instance.refund_requests
    end
  end

  def test_state_and_idempotency_are_enforced
    pending = tools(status: "pending")
    assert_equal :transaction_not_refundable, refund(pending)[:error]

    instance = tools
    assert refund(instance)[:ok]
    assert_equal :duplicate_request, refund(instance)[:error]
    assert_equal 1, instance.refund_requests.length
  end
end
