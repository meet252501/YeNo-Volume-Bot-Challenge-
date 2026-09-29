# Execution Model — Realism the Evaluator Enforces

This is what separates a naive backtest-passing bot from one that
survives the real evaluator. Build against every rule here explicitly.

## 1. 250ms decision-to-fill delay, later book
Every action the bot takes waits 250ms, then crosses a **later** L2
order-book update for its own chosen outcome — not the book snapshot
the bot saw when deciding. An opposite-side book update cannot be
reused either (e.g., seeing a favorable NO-side update doesn't let the
bot fill a YES order against it).

**Implication:** never assume the price you decided on is the price you
get filled at. Build in a tolerance/slippage buffer in the EV
calculation (`docs/algorithms/fee_model.md`), don't treat the observed
book as guaranteed executable.

## 2. Partial fills are real and expected
Displayed depth, minimum order size, split exits, share dust, and
executable one-sided books near expiry are all modeled. **A partial
exit remains part of the same cycle** — it does not close out or reset.

**Implication for `src/cycle_tracker.py`:** track cumulative filled
notional per cycle, not a single fill event. A cycle is "complete" only
when the position is fully closed, however many partial fills that took.

## 3. Writes are ambiguous on timeout
> "A timeout is not permission to retry. Reconcile the venue first or
> risk opening a duplicate position."

**Implementation requirement:** before any retry after a timeout or
uncertain response, the next `/decide` call's `account` state (position,
cash, eligible volume) must be checked against what the bot expects
BEFORE deciding to act again. If the bot's internal expectation and the
evaluator's reported state disagree, trust the evaluator's state, not
the bot's internal assumption — the evaluator is the source of truth.

## 4. Book staleness rejected outright
Books older than 2 seconds are rejected — build the staleness check
(§ Step 1 in `decision_algorithm.md`) as the very first thing evaluated
on every call, before any strategy logic runs.

## 5. Hard timing cutoffs
- No new entries in the final 15 seconds of a market
- Account must be completely flat when the full 24-hour window ends

**Implementation requirement:** the bot needs a persistent sense of "how
much time is left in the overall 24h run," not just per-market
`secondsToClose` — the flatten-by-deadline rule operates on the outer
24h window, not just the current market's own countdown. Track wall-clock
elapsed time since the run began, independent of any single market's timer.

## 6. Causal-only reference data
`reference.observedAt` / `targetObservedAt` / `targetProvisional` exist
specifically so the bot can reason about data recency and provisional
status. **Future-stamped target rows are excluded by the evaluator** —
but the bot should defensively check timestamp ordering itself too,
never assume the evaluator's filtering makes local validation redundant.

## What NOT to do
- Do not design any strategy assuming instant, zero-slippage fills —
  every backtest that doesn't model the 250ms/later-book rule will
  overstate real performance.
- Do not build retry logic that fires automatically on any error without
  a reconciliation step first.
- Do not rely solely on `market.secondsToClose` for the flatten-by-deadline
  rule — that's per-market, the deadline rule is for the whole 24h run.
