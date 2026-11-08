# frozen_string_literal: true

require_relative "test_helper"

class PaymentSimulatorTest < Minitest::Test
  include SafeAgentBenchTestHelpers

  def setup
    @simulator = SafeAgentBench::PaymentSimulator.new(authorization)
  end

  def test_allowed_payment_is_recorded_in_memory
    assert @simulator.submit(transaction(currency: "usd")).allowed?
    assert_equal 1, @simulator.ledger.length
    assert_equal BigDecimal("25.00"), @simulator.total_paid("USD")
  end

  def test_denied_payment_has_no_ledger_side_effect
    decision = @simulator.submit(transaction(recipient: "unknown"))
    assert_equal :recipient_not_authorized, decision.code
    assert_empty @simulator.ledger
  end

  def test_successful_request_cannot_be_replayed
    request = transaction
    assert @simulator.submit(request).allowed?
    assert_equal :duplicate_request, @simulator.submit(request).code
    assert_equal 1, @simulator.ledger.length
  end
end

