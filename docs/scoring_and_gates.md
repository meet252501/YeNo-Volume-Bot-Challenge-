# Scoring & Gates — Internal Mapping

Maps every rule from `docs/challenge_brief_summary.md` to the internal
check that enforces it, so nothing is discovered only at submission time.

## Hard qualification gates → internal enforcement

| Gate | Internal check | Where |
|---|---|---|
| Start with exactly $10, no top-ups/leverage | Backtest harness asserts starting cash == 10.00 before every run | `src/backtest/replay.py` |
| No BUY spends more than $5 (fees included) | `src/risk.py` caps `maxCashUsd` with a safety margin below $5.00; `src/fees.py` output is checked against the cap before the decision is returned | `src/decision.py` |
| ≥$1,000 eligible volume in 24h | `src/cycle_tracker.py` running total, cross-checked against replay report | `src/cycle_tracker.py` |
| Finish completely flat | `src/risk.py` flatten-by-deadline logic; backtest harness flags any non-flat ending as a hard failure, not a partial success | `src/risk.py`, `src/backtest/report.py` |
| At most one open position/pending BUY at a time | `src/decision.py` refuses to return BUY while `account.position` is non-null | `src/decision.py` |
| YeNo BTC 5-min Up/Down only | N/A — enforced by evaluator scope; bot has no other market type to reason about | — |
| Reproducible from immutable commit/container | CI pins exact dependency versions; `docs/SUBMISSION.md` freeze checklist | `.github/workflows/ci.yml` |
| No self-trading / coordinated fills | N/A — bot has no mechanism to identify or coordinate with other entrants; this is a design non-goal, not a check to build | — |

## Ranking tiers → what to optimize, in order

1. **Ending simulated cash** (only among bots that hit $1,000 AND finish
   flat) — this is the primary lever. A bot that qualifies with $9.20
   left outranks one that qualifies with $8.50 left, regardless of how
   it got there.
2. **Max drawdown** (tiebreak only) — don't over-invest engineering time
   here unless tier 1 is already solid; it only matters on an exact cash
   tie, which is unlikely in practice.
3. **Time to target** (final tiebreak) — same caveat; lowest priority of
   the three.

**Practical implication:** almost all optimization effort belongs on
"finish with as much cash left as possible while still crossing $1,000
and ending flat" — not on speed or drawdown minimization for their own
sake.

## Pre-submission checklist (run before every frozen commit)
- [ ] Full 30-path replay run completed, results logged
- [ ] 100% of replay paths finish flat — not "most," all
- [ ] No single BUY across any replay path exceeded $5.00 including fees
- [ ] Stressed run (2-cent adverse execution) still finishes flat on
      every path, even if it doesn't hit $1,000 under stress
- [ ] Bot correctly returns HOLD (not a crash) when books are stale
      (>2s old) or within the final-15-seconds entry cutoff
- [ ] Reconciliation logic tested against a simulated ambiguous-timeout
      scenario — confirm it checks real state before retrying, never
      blindly re-sends a BUY/SELL after a timeout
