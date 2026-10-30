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
| T-013 | Context management in the agent loop: trim and summarize long histories within a token budget; tests with the fake model | T-002 | todo |
| T-014 | Spec Q&A (M5): index public x402 and agent-payment specs; the demo agent can answer questions about them with citations | T-002 | todo |
| T-015 | Retrieval eval for spec Q&A: labeled question set, recall@k, citation correctness; runs in `make check` with a fixed index | T-014, T-011 | todo |
| T-016 | Agent SDK example: the T-002 agent on one agent SDK (OpenAI Agents SDK or Claude Agent SDK), paying only through the guard | T-002 | todo |
| T-017 | Eval report: per run, a safety score (wrong actions that passed the guard) and a usefulness score (correct tasks completed); for each failure, the scenario, the trace, and a suggested fix (e.g. a guard mode or policy change) | T-010, T-011 | todo |
| T-018 | Eval CI mode: exit code on threshold, results saved as JSON, diff against a saved baseline; example GitHub Actions workflow | T-017 | todo |
| T-019 | Custom scenarios guide: `docs/eval-scenarios.md` with the file format, two worked examples (a payment task and a non-payment tool task), and a validator command | T-011 | todo |
| T-029 | Agent connector interface: run the eval against any agent given as a Python callable or reached over MCP; adapters for the raw loop, LangGraph, and the agent SDK; a fake agent for tests | T-011, T-016 | todo |

## Operate (see `docs/operations.md`)

| ID | Task | Depends | Status |
|---|---|---|---|
| T-030 | Dockerfile and health endpoint; container runs the MCP server | T-006 | todo |
| T-031 | Remote MCP over HTTP with API-key auth; each key maps to a policy | T-006, T-030 | todo |
| T-032 | Freeze switch: one config flag or admin call stops all payments; tested | T-031 | todo |
| T-033 | Testnet backend: pay on Base Sepolia through an x402 facilitator | T-003 | todo |
| T-034 | Demo paid API behind an x402 paywall (seller side) | T-033 | todo |
| T-035 | Deploy to a host with config in the repo (one command deploy and rollback); `docs/runbook.md` | T-030, T-032 | todo |
| T-036 | Metrics and alerts: decisions, spend vs. cap, failures, latency (OpenTelemetry) | T-010, T-035 | todo |
| T-037 | Public demo agent on testnet with a daily budget and abuse limits. Small model, sign-in, per-user and global daily LLM spend caps (decision 0004) | T-007, T-034, T-036 | todo |
| T-038 | Kubernetes manifest for self-hosting | T-030 | todo |
| T-039 | Mainnet with a capped operator wallet | T-037 | hold (needs maintainer decision, see decision 0003) |
| T-040 | LLM cost controls for the demo agent: model and caps in config, stop new runs at the cap, cost per request in metrics | T-037 | todo |

## Research-derived (engineering of the maintainer's agent-payment research)

Each lands with its own design note in `docs/` that explains the mechanism without outside material.
`Start` is set by the maintainer; agents do not start a task while it reads `hold`.

| ID | Task | Depends | Start | Status |
|---|---|---|---|---|
| T-020 | Stop one agent among several sharing one account without stopping the others; stop must hold against replay and re-registration | T-004 | hold | todo |
| T-021 | Exposure metrics: separate observed loss, executed amount, and worst-case exposure; scenario families | T-011 | hold | todo |
| T-022 | Sampled verification of paid results: verify a fraction of responses, seller bond, sanctions | T-003 | hold | todo |
| T-023 | Rejection feedback modes: when the guard denies a payment, it can reply with no hint, with the admitted value, with a retry nudge, or hand off to a human. Mode set per policy. Design note `docs/rejection-feedback.md` | T-005 | hold | todo |
| T-024 | Eval: rejection-feedback scenarios. Same task under each mode of T-023; score wrong actions that pass the guard and correct payments completed | T-011, T-023 | hold | todo |
| T-025 | Eval: value-source scenarios. The amount comes from a guard reply, a retrieved document (stale price list or partial policy text, through the T-014 retrieval), or the user's request. Guard option to flag amounts whose only source is retrieved text | T-014, T-024 | hold | todo |
| T-026 | Framework comparison: run T-024 and T-025 on the raw loop (T-002), LangGraph (T-007), and an agent SDK (T-016), with a guard middleware for each; report how each framework returns tool errors and retries | T-007, T-016, T-024 | hold | todo |
| T-027 | Online comparison in the hosted demo: assign a rejection mode per session with a visible notice, within the T-040 caps; metrics for wrong actions and completion | T-023, T-037, T-040 | hold | todo |
| T-028 | Public eval kit: package the scenarios, runner, connector (T-029), report (T-017), and CI mode (T-018) as extra `eval`. The README's first screen states the scope and limits: it measures wrong actions on payment and tool calls, not overall agent quality; passing fixed scenarios is a lower bound, not a proof of safety against adaptive attackers; repeated runs cost model calls on the user's account | T-017, T-018, T-019, T-024, T-029 | hold | todo |

## Log

- 2026-10-28 T-001 done: scaffold with tested policy engine and guard.
- 2026-10-28 Added operations track (T-030 to T-039), context management (T-013), and spec Q&A (T-014).
- 2026-10-30 Added retrieval eval (T-015), agent SDK example (T-016), demo LLM cost controls (T-040), and the rejection-feedback study (T-023 to T-028, start set by the maintainer). Decision 0004.
- 2026-10-30 Added eval kit user requirements: report (T-017), CI mode (T-018), custom scenarios guide (T-019), agent connector (T-029); T-028 now packages them with a scope and limits statement.
