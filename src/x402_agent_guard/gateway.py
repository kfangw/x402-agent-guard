"""Payment backend interface.

The guard decides whether to pay; a backend actually pays. The reference backend
will be an HTTP client for an x402 payment gateway (see docs/tasks.md, T-003).
`FakeBackend` lets tests and examples run without a chain.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from x402_agent_guard.policy import PaymentRequest


@dataclass(frozen=True)
class Receipt:
    tx_ref: str
    amount: int
    asset: str
    payee: str


class PaymentBackend(Protocol):
    def pay(self, req: PaymentRequest) -> Receipt: ...


@dataclass
class FakeBackend:
    paid: list[PaymentRequest] = field(default_factory=list)

    def pay(self, req: PaymentRequest) -> Receipt:
        self.paid.append(req)
        return Receipt(f"fake-{len(self.paid)}", req.amount, req.asset, req.payee)
