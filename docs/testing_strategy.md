# Testing Strategy

## Three layers, each with a different confidence level

### 1. Unit tests (`tests/test_fees.py`, `test_cycle_tracker.py`, `test_risk.py`)
Pure-function tests against known inputs/outputs, including the brief's
own worked examples as golden cases. **Highest confidence** — these
don't depend on external libraries beyond the standard library and
dataclasses, verified runnable even in a constrained sandbox with no
network access (see `NOTES.md` for what was actually executed during
scaffold creation vs. what still needs verification in a real environment).

### 2. Contract tests (`tests/test_decision.py`)
Tests the decision function against the `/decide` schema via
`src/models.py`. **Requires pydantic** — verify these actually pass in
a real environment before trusting them; they were written but not
executed during scaffold creation (see `NOTES.md`).

### 3. Replay/backtest tests (`src/backtest/`)
Full-path simulation against real replay data. **Only as trustworthy as
the replay harness itself** — Phase 0 of `PROJECT_PLAN.md` requires
reproducing the published house-bot benchmark before trusting any
strategy comparison built on top of this layer.

## What "done" means for a strategy change
Per `docs/scoring_and_gates.md` and `docs/learning_harness.md`: a
change is only considered validated when it has passed all three
layers — unit tests still green, contract tests still green, AND a
full replay run (baseline + stressed) showing genuine improvement
without reducing the flat-finish rate below 100%.

## What NOT to do
- Do not consider a strategy "tested" based on unit tests alone — those
  verify the accounting/fee math is correct, not that the strategy
  itself is good.
- Do not skip the stressed-execution replay run "to save time" — a
  strategy untested under stress is unvalidated by this project's own
  standard, not just optimistically assumed fine.
