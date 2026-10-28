"""Policy engine: per-call cap, rolling budget, payee allowlist, approval threshold.

Amounts are integers in the asset's smallest unit (e.g. USDC has 6 decimals),
so no float rounding enters a spending decision.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import StrEnum


class Outcome(StrEnum):
    ALLOW = "allow"
    NEEDS_APPROVAL = "needs_approval"
    DENY = "deny"


@dataclass(frozen=True)
class PaymentRequest:
    agent_id: str
    payee: str
    amount: int
    asset: str
    resource: str = ""
    at: float = 0.0  # unix seconds; supplied by the caller so tests stay deterministic


@dataclass(frozen=True)
class Decision:
    outcome: Outcome
    reason: str

    @property
    def allowed(self) -> bool:
        return self.outcome is Outcome.ALLOW


@dataclass(frozen=True)
class Policy:
    asset: str
    max_per_call: int
    budget: int
    window_seconds: float = 86_400.0
    approval_above: int | None = None
    allowed_payees: frozenset[str] | None = None  # None means any payee


@dataclass
class _Spend:
    at: float
    amount: int


@dataclass
class PolicyEngine:
    """Evaluates requests against one policy per agent and records committed spend.

    `evaluate` never records spend. Call `commit` only after the payment settles,
    so a failed payment does not consume budget.
    """

    policies: dict[str, Policy]
    _spent: dict[str, deque[_Spend]] = field(default_factory=dict)

    def evaluate(self, req: PaymentRequest) -> Decision:
        policy = self.policies.get(req.agent_id)
        if policy is None:
            return Decision(Outcome.DENY, "no policy for agent")
        if req.amount <= 0:
            return Decision(Outcome.DENY, "amount must be positive")
        if req.asset != policy.asset:
            return Decision(Outcome.DENY, f"asset {req.asset} not allowed")
        if policy.allowed_payees is not None and req.payee not in policy.allowed_payees:
            return Decision(Outcome.DENY, "payee not in allowlist")
        if req.amount > policy.max_per_call:
            return Decision(Outcome.DENY, "exceeds per-call cap")
        if self.spent_in_window(req.agent_id, req.at) + req.amount > policy.budget:
            return Decision(Outcome.DENY, "exceeds budget for window")
        if policy.approval_above is not None and req.amount > policy.approval_above:
            return Decision(Outcome.NEEDS_APPROVAL, "above approval threshold")
        return Decision(Outcome.ALLOW, "within policy")

    def commit(self, req: PaymentRequest) -> None:
        self._spent.setdefault(req.agent_id, deque()).append(_Spend(req.at, req.amount))

    def spent_in_window(self, agent_id: str, now: float) -> int:
        policy = self.policies.get(agent_id)
        history = self._spent.get(agent_id)
        if policy is None or not history:
            return 0
        cutoff = now - policy.window_seconds
        while history and history[0].at <= cutoff:
            history.popleft()
        return sum(s.amount for s in history)
