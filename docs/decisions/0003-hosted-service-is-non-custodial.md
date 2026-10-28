# 0003. The hosted service is non-custodial; real money is gated

- Date: 2026-10-28
- Status: accepted

## Context

We want to deploy and operate the guard for real users. A hosted service that pays with
users' funds would hold or move other people's assets, which carries legal and security risk.

## Decision

The hosted service pays only from the operator's own wallet, under a hard daily cap, starting on testnet.
Users who want to use their own funds self-host the container. Mainnet starts only with
explicit maintainer approval recorded as a new decision.

## Consequences

The hosted demo stays small and cheap. Self-hosting must be easy (container, config file).
Agents must not add deposit, custody, or key-import features to the hosted service.
