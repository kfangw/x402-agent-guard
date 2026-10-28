import asyncio

import pytest

pytest.importorskip("mcp")

from x402_agent_guard.mcp_server import create_server  # noqa: E402


def test_server_exposes_payment_tools():
    tools = asyncio.run(create_server().list_tools())
    assert {t.name for t in tools} == {"check_payment", "pay"}


def test_pay_tool_goes_through_guard():
    from x402_agent_guard.gateway import FakeBackend
    from x402_agent_guard.guard import Guard
    from x402_agent_guard.mcp_server import DEMO_AGENT, USDC
    from x402_agent_guard.policy import Policy, PolicyEngine

    backend = FakeBackend()
    guard = Guard(PolicyEngine({DEMO_AGENT: Policy(USDC, 100, 100)}), backend)
    server = create_server(guard)
    asyncio.run(server.call_tool("pay", {"payee": "p", "amount": 60}))
    asyncio.run(server.call_tool("pay", {"payee": "p", "amount": 60}))
    assert [r.amount for r in backend.paid] == [60]
