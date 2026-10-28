# 0003. One implementation of the payment tools

- Date: 2026-10-28
- Status: accepted

## Context

The same tools (`check_payment`, `pay`) reach the model through several front ends:
the MCP server, the plain agent loop, and later LangGraph. Each front end receives
arguments as JSON from a model. If each one parses arguments on its own, one of them
will eventually coerce `"250000"` or `0.25` into a payment, or forget a field check.

## Decision

`tools.PaymentTools` is the only place that turns model arguments into a `PaymentRequest`.
It rejects amounts that are not exactly `int` (including `bool`), empty payees, and unknown
arguments with `ToolError`. Front ends call its methods or `call(name, arguments)`.
The clock is injected so tests are deterministic.

## Consequences

A new front end is a thin adapter. Argument checks change in one file and are tested once.
The agent loop reports `ToolError` back to the model as a tool result instead of raising,
so a malformed call never ends a run and never pays.
