# frozen_string_literal: true

require "bigdecimal"

module SafeAgentBench
  ACTIONS = %i[pay refund].freeze
  DECISION_CODES = %i[
    allowed action_not_authorized currency_not_authorized
    recipient_not_authorized amount_exceeds_limit approval_required
    duplicate_request invalid_amount
  ].freeze

  class Transaction
    attr_reader :request_id, :action, :amount, :currency, :recipient, :human_approved

    def initialize(request_id:, action:, amount:, currency:, recipient:, human_approved: false)
      @request_id = request_id.to_s
      @action = action.to_sym
      @amount = BigDecimal(amount.to_s)
      @currency = currency.to_s.upcase
      @recipient = recipient.to_s
      @human_approved = human_approved
      freeze
    end

    def human_approved?
      human_approved == true
    end
  end

  class Authorization
    attr_reader :allowed_actions, :allowed_currencies, :allowed_recipients,
                :per_transaction_limit, :human_approval_threshold

    def initialize(allowed_actions:, allowed_currencies:, allowed_recipients:,
                   per_transaction_limit:, human_approval_threshold:)
      @allowed_actions = allowed_actions.map { |action| action.to_s.downcase.to_sym }.uniq.freeze
      @allowed_currencies = allowed_currencies.map { |currency| currency.to_s.upcase }.uniq.freeze
      @allowed_recipients = allowed_recipients.map(&:to_s).uniq.freeze
      @per_transaction_limit = BigDecimal(per_transaction_limit.to_s)
      @human_approval_threshold = BigDecimal(human_approval_threshold.to_s)

      validate!
      freeze
    end

    private

    def validate!
      raise ArgumentError, "authorization scope cannot be empty" if
        allowed_actions.empty? || allowed_currencies.empty? || allowed_recipients.empty?
      raise ArgumentError, "limits must be positive" if
        per_transaction_limit <= 0 || human_approval_threshold <= 0
      raise ArgumentError, "approval threshold cannot exceed the transaction limit" if
        human_approval_threshold > per_transaction_limit
    end
  end

  Decision = Struct.new(:allowed, :code, :reason, keyword_init: true) do
    def allowed?
      allowed == true
    end
  end

  LedgerEntry = Struct.new(:request_id, :recipient, :amount, :currency, keyword_init: true)
end

