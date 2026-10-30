# 0004. The hosted guard runs no LLM; the demo agent runs a small model under hard caps

- Date: 2026-10-30
- Status: accepted

## Context

Operating a public agent means paying for model calls on every request, and a public endpoint
can be abused. The guard itself is rule-based and needs no model.

## Decision

The main hosted offering is the guard as a remote MCP server. Users connect their own agents and
pay for their own model calls. We also run one demo agent so visitors can see the whole loop.
The demo agent uses a small model by default, requires sign-in, and has per-user and global daily
LLM spend caps. New runs stop when a cap is reached.

## Consequences

Hosting cost stays near the server bill. Outside users come through the MCP server, which is also
the main operating experience we want. Any change to the demo agent's model or caps goes through
config (T-040), not code. Experiments in the hosted demo (T-027) run inside the same caps.
