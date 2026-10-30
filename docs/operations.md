# Operations plan

The goal is to run this project as a real service with real users, not only publish code.
This file says what runs, where, how we know it is healthy, and what we will not do.

## What runs

| Component | What it is | Who uses it |
|---|---|---|
| Hosted guard (remote MCP) | The MCP server over HTTP. Clients authenticate with an API key. Each key maps to a policy | Developers who connect their agents |
| Demo paid API (seller side) | A small API behind an x402 paywall that we run | Gives agents something real to pay for; produces payment traffic |
| Demo agent | A public agent that uses the hosted guard to pay the demo API, with a daily budget. Runs a small model behind sign-in with daily LLM spend caps (decision 0004) | Visitors who want to see it work |
| Container image | The same guard, self-hosted | Teams who want to run it themselves with their own keys |

## Phases

| Phase | Network | Money | Exit condition |
|---|---|---|---|
| 0. Local | Fake backend | None | `make check` green, container runs locally |
| 1. Testnet | Base Sepolia, test USDC | Test funds only | 30 days up, metrics and runbook in use, at least one outside user |
| 2. Mainnet, capped | Base mainnet, USDC | Operator's own funds, small daily cap | Maintainer approval (see "Hard rules") |

## Hard rules

- **The hosted service never holds other people's funds or keys.** Holding or moving funds for others can be a regulated activity (e.g. virtual asset service rules). Hosted payments come only from the operator's own wallet with a hard daily cap. Users who want to pay with their own funds run the container themselves.
- **Mainnet and real money start only with explicit maintainer approval**, recorded in `docs/decisions/`.
- Keys live in the host's secret store, never in the repository or logs.
- Every hosted key has a policy. No unlimited policy exists in production.

## Health

| Signal | Target (phase 1) |
|---|---|
| Availability of the hosted guard | 99% monthly |
| p95 latency of `check_payment` | < 200 ms |
| Payments that bypass the guard | 0 (by design; alert if the backend sees a payment without a guard decision id) |
| Spend vs. cap | Alert at 80% of the daily cap |

Metrics: requests, decisions by outcome, amount paid, payment failures, latency. Exported with OpenTelemetry.

## Cost

The hosted guard calls no LLM; it costs only hosting. The demo agent calls a model several times per
request (plan, tool calls, reading a denial, answer), so its cost grows with traffic. Rough figures:
a small model is well under one cent per request; a large model can be several cents. Controls (T-040):
small model by default, sign-in, per-user and global daily LLM spend caps, and new runs stop at the cap.
Developers who connect their own agents to the hosted guard pay for their own model calls.

## Runbook and incidents

- `docs/runbook.md`: how to deploy, roll back, rotate keys, freeze all payments.
- `docs/incidents/`: one file per incident: what happened, impact, cause, fix, follow-up tasks.
- The maintainer is on call. A "freeze" switch that stops all hosted payments must exist before phase 1.
