# Decision Log (ADR-style)

Record significant design decisions here as they're made, with the
reasoning — not just the conclusion — so future-you (or a future agent)
doesn't have to re-derive why something is the way it is.

## ADR-001: Fee-curve-aware entry scoring as the primary strategy lever
**Decision:** score entries primarily by distance from 0.50, not just
by directional confidence.
**Reasoning:** verified (docs/RESEARCH.md §1-2) that the fee formula in
the brief matches real Polymarket crypto-market fee documentation
exactly, and that fee cost is structurally lowest near the price
extremes. This is a mechanical fact about the fee curve, not a
backtested-and-hoped-for pattern — it holds regardless of any
particular replay path's quirks.
**Status:** adopted, encoded in `src/fees.py::distance_from_mid` and
`src/decision.py::entry_score`.

## ADR-002: Apply a haircut to near-certain prices rather than trusting them at face value
**Decision:** subtract a fixed haircut from confidence scoring when
price is ≥0.85 or ≤0.15.
**Reasoning:** documented academic finding (docs/RESEARCH.md §4) that
heavy favorites resolve slightly less often than price implies.
**Status:** adopted, encoded in `src/risk.py::confidence_haircut`.
Value (0.03) is a starting estimate, not derived from this project's
own data — tune against real replay results once available.

## ADR-003: Flatten-by-deadline is checked before all other decision logic, unconditionally
**Decision:** `must_flatten_now` is the very first check in
`decide()`, overriding entry/exit strategy entirely.
**Reasoning:** the qualification rules make a non-flat ending a total
failure regardless of ending cash — asymmetric downside means this
check should never be subject to strategy-level judgment calls.
**Status:** adopted.

## ADR-004: Backtest harness fails loudly rather than returning placeholder numbers
**Decision:** `src/backtest/replay.py::run_replay_path` raises
`NotImplementedError` until wired to real replay data, instead of
returning fabricated placeholder results.
**Reasoning:** matches this project's own standard (see
`docs/RESEARCH.md`, `docs/learning_harness.md`) of never reporting
invented numbers as if they were real — a silently-fake backtest result
would be worse than an obvious failure.
**Status:** adopted; revisit once Phase 0 (real replay data) is complete.

## ADR-005: Corrected price-band from unbounded "prefer extremes" to bounded 0.30-0.80
**Decision:** entry scoring now hard-gates on a 0.30-0.80 price band,
rejecting entries outside it entirely, rather than monotonically
preferring distance from 0.50 without limit.
**Reasoning:** a real competitor's out-of-sample-tested swept-band data
(see docs/RESEARCH.md §7b, docs/competitor_repos.md) found entries above
~0.90 actually lost money on the week — the fee curve being cheapest at
the extremes does not mean the extremes are most profitable, since the
real edge (mispricing) also shrinks near the extremes. This corrects
ADR-002's original, narrower "haircut near 0.85/0.15" approach, which
was directionally aware of the risk but didn't go far enough — it still
implicitly treated 0.90 as scoring higher than 0.50, which the real data
contradicts.
**Status:** adopted. `src/risk.py::in_tested_profitable_band` and
`confidence_haircut` updated; `src/decision.py::entry_score` now gates
on the band before scoring. Verified with pure-Python tests (see
NOTES.md) — the corrected logic was confirmed to actually change the
scoring outcome for a 0.90 entry, not just documented as a good idea.

## ADR-006: Settlement modeled as a 60s TWAP, not last-price
**Decision:** treat settlement as mean-of-last-60s vs. mean-of-60s-before-open.
**Reasoning:** real tested data (docs/algorithms/settlement_mechanics.md)
shows this definition matches real winners 98.0% of the time vs. 87.3%
for a naive last-price comparison, across 2,014 real markets.
**Status:** documented as a design input; not yet encoded into
`src/decision.py`'s exit logic — next implementation step, not yet done.
