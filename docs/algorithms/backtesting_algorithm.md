# Backtesting Algorithm — `src/backtest/`

## Goal
Reproduce Builderr's own published house-bot benchmark methodology
closely enough that local numbers are trustworthy, and be honest about
where backtest confidence is warranted vs. not (per docs/RESEARCH.md §6).

## Methodology split: hold-to-expiry vs. path-dependent logic
Per the research finding from a real Kalshi paper-trading bot's
methodology: **hold-to-expiry strategies can be backtested with full
statistical confidence against historical replay data.** Path-dependent
strategies (e.g., an in-flight stop-loss reacting to live book movement
mid-position) generally cannot be reliably backtested against
coarse-grained replay data — the replay data's resolution may not
capture the exact intra-cycle path a live order book would show.

**Rule for this project:** if the strategy stays hold-to-expiry-style
(enter, then exit only at resolution or at the flatten deadline), trust
the backtest numbers directly. If any path-dependent exit logic is ever
added (react mid-position to book movement before resolution), flag its
backtest results as directional/illustrative only in trial logs, not as
confirmed performance — don't let a good-looking number there create
false confidence.

## Replay report shape (match Builderr's own published format)
```python
@dataclass
class ReplayReport:
    path_results: list[float]  # ending cash per path
    flat_count: int  # paths that ended flat
    total_paths: int
    hit_target_count: int  # paths that crossed $1,000
    stressed_path_results: list[float]  # under 2-cent adverse execution
    median: float
    best: float
    worst: float
    median_among_flat: float
```

## Stress testing — non-optional
Every strategy change must be evaluated under both:
1. **Baseline execution** (replay data as recorded)
2. **2-cent adverse-execution stress** — simulate every fill landing 2
   cents worse than the recorded book would suggest, matching the
   stress test methodology the brief itself published results for
   (best fell to $385, median to $70, on the house bot)

A strategy that only looks good under baseline execution and collapses
under stress is not actually an improvement — report both numbers side
by side in every trial log entry, never baseline alone.

## Reproducing the house bot benchmark first (Phase 0 requirement)
Before any strategy modification, run the included House Bot v1 against
the local replay set and confirm the numbers are in the same
neighborhood as the published benchmark ($559 median, $943 best, 18/30
flat). If local numbers diverge significantly, the backtest harness
itself likely has a bug — fix that before trusting any strategy
comparison built on top of it.

## What NOT to do
- Do not report only best-case or only baseline numbers in a trial log
  — always report median, worst, and stressed alongside best.
- Do not treat a strategy that's overfit to the specific 30 development
  paths as validated — the real qualification run uses a different,
  unseen window (see `docs/learning_harness.md`).
- Do not skip reproducing the house-bot baseline "to save time" — an
  unverified backtest harness makes every subsequent number meaningless.
