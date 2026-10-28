"""Agent loop without a framework (task T-002).

Runs a scripted model against the guard and a fake backend, so it needs no API key:

    python examples/raw_agent_loop.py

The script plays an agent that buys one report, then is talked into a second, larger
payment by text in a tool result. The guard holds the second one for approval.
To use a real model, write a class with `complete(messages, tools) -> ModelTurn` that
calls your provider's tool-calling API, and pass it to `run_agent` instead.
"""

from x402_agent_guard.agent import ModelTurn, ScriptedModel, ToolCall, run_agent
from x402_agent_guard.gateway import FakeBackend
from x402_agent_guard.guard import Guard
from x402_agent_guard.policy import Policy, PolicyEngine
from x402_agent_guard.tools import PaymentTools


def main() -> None:
    policy = Policy(asset="USDC", max_per_call=1_000_000, budget=5_000_000, approval_above=500_000)
    backend = FakeBackend()
    tools = PaymentTools(Guard(PolicyEngine({"agent-1": policy}), backend), "agent-1", "USDC")
    model = ScriptedModel(
        [
            ModelTurn(
                "Buying the report.",
                (ToolCall("c1", "pay", {"payee": "0xReports", "amount": 250_000}),),
            ),
            ModelTurn(
                "The seller says a premium tier is required.",
                (ToolCall("c2", "pay", {"payee": "0xReports", "amount": 900_000}),),
            ),
            ModelTurn("Bought the report; the premium payment is waiting for approval."),
        ]
    )
    run = run_agent(model, tools, "Buy today's market report.")
    for m in run.messages:
        print(f"{m.role:9} {m.content}")
        for c in m.tool_calls:
            print(f"{'':9} -> {c.name}({c.arguments})")
    print(f"stopped: {run.stopped}; backend paid {[r.amount for r in backend.paid]}")


if __name__ == "__main__":
    main()
