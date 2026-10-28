# x402-agent-guard

Guardrails for LLM agents that pay over [x402](https://www.x402.org/).

An agent that can call a paid API can also be talked into paying for the wrong thing.
This project puts a small, testable layer between the agent and the money:

- **Limits.** Per-call cap, rolling budget, payee allowlist, per agent.
- **Approval.** Payments above a threshold stop and wait for a human.
- **One path to pay.** Tools exposed to the model can only pay through the guard.
- **Evaluation** (planned). Run an agent through adversarial scenarios and measure how much it would have paid.

Status: early scaffold. The policy engine and guard work and are tested. The MCP server
runs against a fake backend. See [docs/tasks.md](docs/tasks.md) for what comes next.

## Quick start

```bash
make setup     # pip install -e ".[dev,mcp]"
make check     # lint + tests
x402-agent-guard-mcp   # MCP server over stdio, demo policy, fake backend
```

```python
from x402_agent_guard import PaymentRequest, Policy, PolicyEngine
from x402_agent_guard.gateway import FakeBackend
from x402_agent_guard.guard import Guard

policy = Policy(asset="USDC", max_per_call=1_000_000, budget=5_000_000, approval_above=500_000)
guard = Guard(PolicyEngine({"agent-1": policy}), FakeBackend())
result = guard.request_payment(PaymentRequest("agent-1", "0xPayee", 250_000, "USDC"))
print(result.decision.outcome, result.receipt)
```

Amounts are integers in the asset's smallest unit (USDC: 6 decimals).

## Layout

```
src/x402_agent_guard/
  policy/        policy engine (M2: limits, approval threshold)
  guard.py       the only path from a tool call to a payment
  gateway.py     payment backend interface and a fake backend
  mcp_server.py  MCP tools: check_payment, pay (M1)
  eval/          exposure evaluation (M3, planned)
examples/        agent loops with and without a framework
docs/            design, task list, decision records
```

## Operations

This project is run as a service, testnet first. Plan, health targets, and hard rules: [docs/operations.md](docs/operations.md).

## How this project is developed

Most changes are written by coding agents and reviewed by a human.
The rules agents follow are in [AGENTS.md](AGENTS.md); they apply to human contributors too.

## License

MIT
