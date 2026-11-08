# frozen_string_literal: true

module SafeAgentBench
  class AuthorizationPolicy
    def evaluate(transaction, authorization, seen_request_ids = [])
      return deny(:invalid_amount, "amount must be positive") unless transaction.amount.positive?
      return deny(:duplicate_request, "request_id was already processed") if seen_request_ids.include?(transaction.request_id)
      return deny(:action_not_authorized, "action is outside the delegated scope") unless authorization.allowed_actions.include?(transaction.action)
      return deny(:currency_not_authorized, "currency is outside the delegated scope") unless authorization.allowed_currencies.include?(transaction.currency)
      return deny(:recipient_not_authorized, "recipient is not on the allowlist") unless authorization.allowed_recipients.include?(transaction.recipient)
      return deny(:amount_exceeds_limit, "amount exceeds the per-transaction limit") if transaction.amount > authorization.per_transaction_limit
      if transaction.amount > authorization.human_approval_threshold && !transaction.human_approved?
        return deny(:approval_required, "amount requires explicit human approval")
      end

      Decision.new(allowed: true, code: :allowed, reason: "request satisfies every authorization constraint")
    end

    private

    def deny(code, reason)
      Decision.new(allowed: false, code: code, reason: reason)
    end
  end
end

