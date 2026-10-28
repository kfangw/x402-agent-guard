# AGENTS.md

Rules for anyone changing this repository: coding agents (Claude Code, Codex, others) and humans.
This project is developed agent-first. A human sets direction and reviews; agents do most of the work.
Everything an agent needs to work here must be in this repository, in plain files.

## Start here

1. Read `README.md`, then `docs/design.md`.
2. Pick work from `docs/tasks.md`. Take the first `todo` task whose dependencies are `done`, unless you were given one.
3. Run `make check` before you change anything. It must pass at the start and at the end.

## Workflow for one task

1. Mark the task `doing` in `docs/tasks.md` with the date.
2. Write or update tests first when the change has behavior.
3. Make the smallest change that completes the task. Do not widen scope; add a new task instead.
4. Run `make check`. Fix until it passes. Do not skip, delete, or weaken tests to get green.
5. Mark the task `done`, add one line under "Log" in `docs/tasks.md`, and commit.
6. If you made a design choice others must follow, add a record in `docs/decisions/` (copy `0000-template.md`).

## Code rules

- Python 3.11+. Format and lint with ruff (`make fmt`). Line length 100.
- Money is `int` in the asset's smallest unit. Never `float` for amounts.
- Time is passed in, not read inside the policy engine, so tests stay deterministic.
- `Guard.request_payment` is the only path to `PaymentBackend.pay`. New tools must go through it.
- `PolicyEngine.evaluate` must not change state. Only `commit` records spend, and only after payment succeeds.
- Core modules (`policy/`, `guard.py`) have no network or LLM dependencies. Optional integrations go behind extras in `pyproject.toml`.
- No secrets in the repository. Keys come from environment variables. Tests never touch a real chain or a paid API.

## Commits

- One task per commit when possible. Message: `T-xxx: what changed` in English, imperative mood.
- Do not rewrite published history. No force push to `main`.

## Self-contained

This repository must stand on its own. Someone with only this repository can build it,
test it, and understand why each mechanism exists.

- Research results (from the maintainer's work on agent payments) are welcome here as engineering:
  limits, revocation, settlement verification, exposure measurement.
  Bring each one in as code, tests, and an explanation in `docs/` written for this repository.
- Do not depend on, link to, or copy paths from private repositories. Cite only public papers and specs.
- No personal information, no job-search material, no secrets.
- The maintainer decides when a research-derived task starts (the `Start` column in `docs/tasks.md`).
