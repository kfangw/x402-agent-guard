import asyncio

import pytest

pytest.importorskip("mcp")

from x402_agent_guard.mcp_server import create_server  # noqa: E402


def test_server_exposes_payment_tools():
    tools = asyncio.run(create_server().list_tools())
    assert {t.name for t in tools} == {"check_payment", "pay"}
