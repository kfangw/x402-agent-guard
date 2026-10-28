from x402_agent_guard.policy import Outcome, PaymentRequest, Policy, PolicyEngine

USDC = "USDC"


def engine(**kw):
    base = dict(asset=USDC, max_per_call=100, budget=250, window_seconds=60)
    base.update(kw)
    return PolicyEngine({"a": Policy(**base)})


def req(amount, at=0.0, payee="p", agent="a", asset=USDC):
    return PaymentRequest(agent, payee, amount, asset, at=at)


def test_allows_within_policy():
    assert engine().evaluate(req(50)).outcome is Outcome.ALLOW


def test_denies_unknown_agent_bad_asset_and_nonpositive():
    e = engine()
    assert e.evaluate(req(10, agent="x")).outcome is Outcome.DENY
    assert e.evaluate(req(10, asset="DAI")).outcome is Outcome.DENY
    assert e.evaluate(req(0)).outcome is Outcome.DENY


def test_per_call_cap():
    assert engine().evaluate(req(101)).reason == "exceeds per-call cap"


def test_budget_counts_only_committed_spend_in_window():
    e = engine()
    for t in (0, 1):
        r = req(100, at=t)
        assert e.evaluate(r).allowed
        e.commit(r)
    assert e.evaluate(req(60, at=2)).reason == "exceeds budget for window"
    assert e.evaluate(req(50, at=2)).allowed
    # first spend at t=0 leaves the 60 s window at t=60
    assert e.evaluate(req(100, at=60)).allowed


def test_evaluate_does_not_record_spend():
    e = engine()
    for _ in range(5):
        e.evaluate(req(100))
    assert e.spent_in_window("a", 0) == 0


def test_allowlist_and_approval_threshold():
    e = engine(allowed_payees=frozenset({"ok"}), approval_above=40)
    assert e.evaluate(req(10, payee="bad")).reason == "payee not in allowlist"
    assert e.evaluate(req(50, payee="ok")).outcome is Outcome.NEEDS_APPROVAL
    assert e.evaluate(req(40, payee="ok")).outcome is Outcome.ALLOW
