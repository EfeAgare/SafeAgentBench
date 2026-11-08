# frozen_string_literal: true

require_relative "test_helper"

class AgentTest < Minitest::Test
  def build_agent(refunds: [], max_steps: 4, model: SafeAgentBench::OfflineMockModel.new)
    tools = SafeAgentBench::TransactionTools.new
    policy = SafeAgentBench::ToolAuthorizationPolicy.new(
      allowed_tools: %i[lookup_transaction request_refund], refund_transaction_ids: refunds
    )
    [SafeAgentBench::ToolCallingAgent.new(model: model, tools: tools, policy: policy, max_steps: max_steps), tools]
  end

  def test_lookup_uses_the_offline_model
    agent, = build_agent
    result = agent.run("Find TX-1001")
    assert_equal :completed, result.status
    assert_includes result.text, "42.50 USD"
  end

  def test_refund_is_denied_without_independent_authorization
    agent, tools = build_agent
    result = agent.run("Refund TX-1001")
    assert_includes result.text, "refund_not_authorized"
    assert_empty tools.refund_requests
  end

  def test_authorized_refund_is_simulated
    agent, tools = build_agent(refunds: ["TX-1001"])
    result = agent.run("Refund TX-1001")
    assert_includes result.text, "simulated successfully"
    assert_equal :simulated_requested, tools.refund_requests.first[:status]
  end

  def test_agent_loop_is_bounded
    looping_model = Class.new do
      def respond(_messages)
        SafeAgentBench::ModelResponse.new(
          tool_call: SafeAgentBench::ToolCall.new(name: :lookup_transaction, arguments: { transaction_id: "TX-1001" })
        )
      end
    end.new
    agent, = build_agent(model: looping_model, max_steps: 2)
    result = agent.run("loop")
    assert_equal :max_steps_exceeded, result.status
    assert_equal 2, result.steps
  end
end

