"""Guard: policy check, then pay, then commit spend. The only path to a payment."""

from __future__ import annotations

from dataclasses import dataclass

from x402_agent_guard.gateway import PaymentBackend, Receipt
from x402_agent_guard.policy import Decision, Outcome, PaymentRequest, PolicyEngine


@dataclass(frozen=True)
class GuardResult:
    decision: Decision
    receipt: Receipt | None = None


@dataclass
class Guard:
    engine: PolicyEngine
    backend: PaymentBackend

    def request_payment(self, req: PaymentRequest, approved: bool = False) -> GuardResult:
        decision = self.engine.evaluate(req)
        if decision.allowed or (approved and decision.outcome is Outcome.NEEDS_APPROVAL):
            receipt = self.backend.pay(req)
            self.engine.commit(req)
            return GuardResult(decision, receipt)
        return GuardResult(decision)
