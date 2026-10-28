# Tasks

Status: `todo`, `doing (YYYY-MM-DD)`, `done`, `blocked (reason)`.
Agents pick the first `todo` task whose dependencies are `done`. Keep tasks small: one commit each.

## Now

| ID | Task | Depends | Status |
|---|---|---|---|
| T-001 | Scaffold: policy engine, guard, fake backend, MCP server, CI | | done |
| T-002 | `examples/raw_agent_loop.py`: agent loop with plain LLM API tool calling, no framework. Provider-agnostic interface; a scripted fake model for tests | T-001 | todo |
| T-003 | HTTP backend for an x402 payment gateway (`gateway.py`). Config from env. Tests use a mocked transport | T-001 | todo |
| T-004 | Persist spend history (SQLite) so budgets survive restarts | T-001 | todo |
| T-005 | Approval flow: `needs_approval` returns a pending id; a separate `approve(id)` path pays. MCP tool for listing pending payments | T-001 | todo |
| T-006 | MCP server config: load policies from a TOML file instead of the demo policy | T-001 | todo |
| T-008 | Move to mcp 2.x (`FastMCP` renamed `MCPServer`); drop the `<2` pin in `pyproject.toml` | T-001 | todo |
| T-007 | `examples/langgraph_agent.py`: same agent as T-002 on LangGraph, with an interrupt before payments | T-002, T-005 | todo |

## Next

| ID | Task | Depends | Status |
|---|---|---|---|
| T-010 | Tracing: OpenTelemetry spans for each tool call, decision, and payment (extra `otel`) | T-002 | todo |
| T-011 | Eval harness skeleton: scenario file format, runner, score = amount paid outside user intent | T-002 | todo |
| T-012 | First scenario set: injected instructions in tool results asking the agent to pay | T-011 | todo |

## Research-derived (engineering of the maintainer's agent-payment research)

Each lands with its own design note in `docs/` that explains the mechanism without outside material.
`Start` is set by the maintainer; agents do not start a task while it reads `hold`.

| ID | Task | Depends | Start | Status |
|---|---|---|---|---|
| T-020 | Stop one agent among several sharing one account without stopping the others; stop must hold against replay and re-registration | T-004 | hold | todo |
| T-021 | Exposure metrics: separate observed loss, executed amount, and worst-case exposure; scenario families | T-011 | hold | todo |
| T-022 | Sampled verification of paid results: verify a fraction of responses, seller bond, sanctions | T-003 | hold | todo |

## Log

- 2026-10-28 T-001 done: scaffold with tested policy engine and guard.
- 2026-10-28 Makefile runs ruff and pytest via `python -m` so `make check` uses the installed package.
