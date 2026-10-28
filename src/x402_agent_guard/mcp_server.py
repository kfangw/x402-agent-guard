"""MCP server exposing guarded payments as tools (module M1).

Run with `x402-agent-guard-mcp` after `pip install -e ".[mcp]"`.
The server uses a FakeBackend and a demo policy until T-003 lands.
"""

from __future__ import annotations

from x402_agent_guard.gateway import FakeBackend
from x402_agent_guard.guard import Guard
from x402_agent_guard.policy import Policy, PolicyEngine
from x402_agent_guard.tools import PaymentTools

DEMO_AGENT = "demo-agent"
USDC = "USDC"


def build_guard() -> Guard:
    policy = Policy(asset=USDC, max_per_call=1_000_000, budget=5_000_000, approval_above=500_000)
    return Guard(PolicyEngine({DEMO_AGENT: policy}), FakeBackend())


def create_server(guard: Guard | None = None):
    from mcp.server.fastmcp import FastMCP

    tools = PaymentTools(guard or build_guard(), DEMO_AGENT, USDC)
    server = FastMCP("x402-agent-guard")

    @server.tool()
    def check_payment(payee: str, amount: int, resource: str = "") -> dict:
        """Check whether a payment would be allowed. Amount is in USDC base units (6 decimals)."""
        return tools.check_payment(payee, amount, resource)

    @server.tool()
    def pay(payee: str, amount: int, resource: str = "") -> dict:
        """Pay if policy allows. Payments that need approval are refused here; a human approves."""
        return tools.pay(payee, amount, resource)

    return server


def main() -> None:
    create_server().run()


if __name__ == "__main__":
    main()
