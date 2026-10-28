from x402_agent_guard.gateway import FakeBackend
from x402_agent_guard.guard import Guard
from x402_agent_guard.policy import Outcome, PaymentRequest, Policy, PolicyEngine


def make():
    policy = Policy(asset="USDC", max_per_call=100, budget=150, approval_above=80)
    backend = FakeBackend()
    return Guard(PolicyEngine({"a": policy}), backend), backend


def r(amount):
    return PaymentRequest("a", "p", amount, "USDC")


def test_denied_payment_never_reaches_backend():
    guard, backend = make()
    assert guard.request_payment(r(500)).receipt is None
    assert backend.paid == []


def test_allowed_payment_pays_and_commits():
    guard, backend = make()
    assert guard.request_payment(r(70)).receipt is not None
    assert guard.engine.spent_in_window("a", 0) == 70
    assert guard.request_payment(r(90)).decision.reason == "exceeds budget for window"
    assert len(backend.paid) == 1


def test_approval_required_unless_approved():
    guard, backend = make()
    res = guard.request_payment(r(90))
    assert res.decision.outcome is Outcome.NEEDS_APPROVAL and res.receipt is None
    assert guard.request_payment(r(90), approved=True).receipt is not None
    assert len(backend.paid) == 1
