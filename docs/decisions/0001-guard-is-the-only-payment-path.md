# 0001. The guard is the only path to a payment

- Date: 2026-10-28
- Status: accepted

## Context

Agents get payment ability through tools. If any tool can call the backend directly,
one forgotten check bypasses every limit.

## Decision

Only `Guard.request_payment` calls `PaymentBackend.pay`. The policy engine is pure and
records spend only through `commit`, called after a successful payment.

## Consequences

New tools and examples must construct a `PaymentRequest` and go through the guard.
Failed payments do not consume budget. Spend tracking lives in one place.
