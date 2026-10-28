# Design

## Problem

LLM agents increasingly pay for APIs and data with x402: the server answers `402 Payment Required`,
the client signs a stablecoin payment, and retries. The model decides when to call a paid tool.
A prompt injection, a confused plan, or a loop can turn that into unwanted spending.
The payment rail itself does not know what the user intended.

## Approach

Put a guard between the model's tool calls and the payment backend.

```
LLM ──tool call──▶ MCP tool / agent loop ──PaymentRequest──▶ Guard ──▶ PaymentBackend ──▶ x402 gateway
                                                              │
                                                       PolicyEngine (limits, allowlist, approval)
```

- **PolicyEngine** is pure: request in, decision out (`allow`, `needs_approval`, `deny`).
- **Guard** is the only caller of the backend. It commits spend only after a payment succeeds.
- **PaymentBackend** is an interface. `FakeBackend` for tests; an HTTP client for a real x402 gateway next.

## Modules

| Module | What | Status |
|---|---|---|
| M1 | MCP server exposing guarded payment tools; agent loop examples (no framework, LangGraph) | MCP server on fake backend; examples todo |
| M2 | Policy: per-call cap, rolling budget, allowlist, approval threshold, per-agent policies; later, stopping one agent among many | basic done; stop planned (research-derived) |
| M3 | Exposure evaluation: scenario suite, run an agent, score money at risk; OpenTelemetry traces | planned (research-derived) |
| M4 | Settlement verification: sample-check paid results, bonds and sanctions | planned (research-derived) |
| M5 | Q&A over x402 and agent-payment specs (RAG), used by the demo agent | planned (T-014) |

## Operations

The project is meant to be deployed and operated. See `docs/operations.md`.

## Non-goals (for now)

- Custody of other people's funds. The hosted service pays only from the operator's capped wallet (decision 0003).
- On-chain enforcement. Limits here are off-chain, in the agent's process.
