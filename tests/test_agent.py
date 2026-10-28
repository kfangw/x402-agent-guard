import json

import pytest

from x402_agent_guard.agent import ModelTurn, ScriptedModel, ToolCall, run_agent
from x402_agent_guard.gateway import FakeBackend
from x402_agent_guard.guard import Guard
from x402_agent_guard.policy import Policy, PolicyEngine
from x402_agent_guard.tools import PaymentTools, ToolError


def make():
    policy = Policy(asset="USDC", max_per_call=100, budget=150, approval_above=80)
    backend = FakeBackend()
    guard = Guard(PolicyEngine({"a": policy}), backend)
    return PaymentTools(guard, "a", "USDC", clock=lambda: 0.0), backend


def pay(call_id, amount, **extra):
    return ToolCall(call_id, "pay", {"payee": "p", "amount": amount, **extra})


def tool_results(run):
    return [json.loads(m.content) for m in run.messages if m.role == "tool"]


def test_answer_without_tool_call_stops():
    tools, backend = make()
    run = run_agent(ScriptedModel([ModelTurn("hi")]), tools, "hello")
    assert (run.stopped, run.answer) == ("answered", "hi")
    assert backend.paid == []


def test_payments_go_through_guard_and_results_reach_model():
    tools, backend = make()
    model = ScriptedModel([ModelTurn(tool_calls=(pay("1", 50), pay("2", 90))), ModelTurn("done")])
    run = run_agent(model, tools, "buy")
    first, second = tool_results(run)
    assert first["outcome"] == "allow" and "tx_ref" in first
    assert second == {"outcome": "needs_approval", "reason": "above approval threshold"}
    assert [r.amount for r in backend.paid] == [50]
    # the model's second turn sees both tool results, linked to their calls
    last_seen = model.seen[-1]
    assert [m.tool_call_id for m in last_seen if m.role == "tool"] == ["1", "2"]


def test_check_payment_does_not_pay():
    tools, backend = make()
    call = ToolCall("1", "check_payment", {"payee": "p", "amount": 50})
    run = run_agent(ScriptedModel([ModelTurn(tool_calls=(call,)), ModelTurn("ok")]), tools, "x")
    assert tool_results(run) == [{"outcome": "allow", "reason": "within policy"}]
    assert backend.paid == []


@pytest.mark.parametrize(
    "call",
    [
        ToolCall("1", "transfer", {"payee": "p", "amount": 1}),
        ToolCall("1", "pay", {"payee": "p", "amount": "50"}),
        ToolCall("1", "pay", {"payee": "p", "amount": 0.5}),
        ToolCall("1", "pay", {"payee": "p", "amount": True}),
        ToolCall("1", "pay", {"payee": "", "amount": 5}),
        ToolCall("1", "pay", {"amount": 5}),
        ToolCall("1", "pay", {"payee": "p", "amount": 5, "asset": "DAI"}),
    ],
)
def test_bad_tool_calls_become_errors_not_payments(call):
    tools, backend = make()
    run = run_agent(ScriptedModel([ModelTurn(tool_calls=(call,)), ModelTurn("ok")]), tools, "x")
    assert run.stopped == "answered"
    assert "error" in tool_results(run)[0]
    assert backend.paid == []


def test_step_limit_bounds_a_looping_model():
    tools, backend = make()
    model = ScriptedModel([ModelTurn(tool_calls=(pay(str(i), 10),)) for i in range(10)])
    run = run_agent(model, tools, "x", max_steps=3)
    assert run.stopped == "step_limit" and run.answer == ""
    assert len(backend.paid) == 3


def test_tools_call_rejects_non_object_arguments():
    tools, _ = make()
    with pytest.raises(ToolError):
        tools.call("pay", ["p", 5])


def test_example_runs(capsys):
    from importlib.util import module_from_spec, spec_from_file_location
    from pathlib import Path

    path = Path(__file__).parent.parent / "examples" / "raw_agent_loop.py"
    spec = spec_from_file_location("raw_agent_loop", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()
    assert "backend paid [250000]" in capsys.readouterr().out
