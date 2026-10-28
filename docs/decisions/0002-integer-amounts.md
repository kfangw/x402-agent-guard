# 0002. Amounts are integers in base units

- Date: 2026-10-28
- Status: accepted

## Context

Stablecoins have fixed decimals (USDC: 6). Floats make budget comparisons inexact.

## Decision

All amounts are `int` in the asset's smallest unit. Conversion to display units happens only at the edges.

## Consequences

Tool schemas take integers. Examples must state the unit.
