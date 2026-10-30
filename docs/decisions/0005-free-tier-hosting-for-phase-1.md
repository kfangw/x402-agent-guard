# 0005. Phase 1 runs on free tiers: Cloud Run, a testnet facilitator, and a free model API

- Date: 2026-10-30
- Status: accepted

## Context

Phase 1 (testnet, see `docs/operations.md`) must run for 30 days with outside users while
costing close to nothing. The guard calls no LLM (decision 0004); only the demo agent does.
Free tiers change often, so each choice below records how it was checked and what replaces it.

## Decision

| Component | Choice | Free terms as checked | Checked | Fallback |
|---|---|---|---|---|
| Hosting for the guard (remote MCP) and the demo paid API | Google Cloud Run, two services from the T-030 image | 2M requests, 180,000 vCPU-seconds, 360,000 GB-seconds per month; card required | Third-party comparison checked against official pages on 2026-09-16; the official pricing page did not load for us | Any container host; the image and config do not depend on Cloud Run |
| Facilitator | x402.org facilitator to start; CDP facilitator when we need keys and metrics | x402.org: testnet only, no API key. CDP: Base Sepolia supported; 1,000 onchain transactions per month free, then $0.001 each; verification always free | CDP terms from the official CDP page (2026-10-30); x402.org terms from a third-party guide | Either one; both speak the same protocol |
| Test funds | Circle faucet for test USDC on Base Sepolia; CDP or Alchemy faucet for ETH | Free | Third-party guide (2026-10-30) | Other Base Sepolia faucets |
| Demo agent model | A small model on a free API tier (Groq first) | Free-tier limits are per organization and shown in the provider console, not on the public page | Provider docs (2026-10-30) show only paid-tier tables | Gemini Flash free tier (check data-use terms) or OpenRouter free models; T-040 caps hold in all cases |
| Spend history (T-004) and retrieval vectors (T-014) | A hosted Postgres with pgvector on a free tier | Not chosen yet | - | SQLite in a volume when the host offers one |
| Telemetry | An OpenTelemetry receiver with a free tier | Not chosen yet | - | Logs only |

Operating rules that come with this choice:

- Set a billing budget alert (for example 1 USD) on every account that holds a card.
- Cloud Run scales to zero, so the first request after idle is slow. In phase 1 the latency
  target in `docs/operations.md` applies to warm instances. Keeping one instance always on is a
  paid change and needs a new decision.
- Use a separate operator wallet for the hosted service. Never reuse keys from other projects.
- Re-check free terms before deploy (T-035) and when a provider announces changes.

## Consequences

Phase 1 can run at close to zero cost. The deploy (T-035) targets Cloud Run but keeps the
container portable. The demo agent's model can change with config only (T-040). If a free tier
ends, we move the affected component to its fallback and record the change as a new decision.
