# frozen_string_literal: true

module SafeAgentBench
  class PaymentSimulator
    attr_reader :authorization

    def initialize(authorization, policy: AuthorizationPolicy.new)
      @authorization = authorization
      @policy = policy
      @ledger = []
    end

    def ledger
      @ledger.dup.freeze
    end

    def submit(transaction)
      decision = @policy.evaluate(transaction, authorization, @ledger.map(&:request_id))
      if decision.allowed?
        @ledger << LedgerEntry.new(
          request_id: transaction.request_id,
          recipient: transaction.recipient,
          amount: transaction.amount,
          currency: transaction.currency
        )
      end
      decision
    end

    def total_paid(currency)
      normalized = currency.to_s.upcase
      @ledger.select { |entry| entry.currency == normalized }.sum(BigDecimal("0"), &:amount)
    end
  end
end

