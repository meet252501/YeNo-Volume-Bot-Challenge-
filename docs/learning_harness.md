# Learning Harness

The try → score → promote → freeze loop for strategy iteration.

## Loop

1. **Try** — run a candidate strategy change against the full local
   replay set (all available development paths, not a handful)
2. **Score** — record per trial:
   - median / best / worst ending cash across all paths
   - % of paths finishing flat
   - % of paths crossing $1,000
   - stressed-run numbers (2-cent adverse execution) — median and worst
   - max drawdown observed
3. **Promote** — keep a change only if it improves the median AND does
   not reduce the flat-finish rate below 100%. A strategy that
   occasionally fails to flatten is disqualifying in the real
   evaluation regardless of how good its median looks — never trade
   flat-rate for median performance.
4. **Freeze** — lock a commit only after a full clean run; see
   `docs/SUBMISSION.md`.

## Trial log format

```
trial_id, date, change_description, median_cash, best_cash, worst_cash,
pct_flat, pct_hit_target, stressed_median, stressed_worst, max_drawdown,
promoted (bool), notes
```

## Important constraint

The **real qualification run uses one unseen, receive-time-ordered
24-hour window** — not the published replay set. A strategy that's
overfit to quirks of the specific 30 development paths (rather than to
the underlying fee/execution mechanics) risks looking great locally and
failing on the real unseen window. Prefer changes justified by the
mechanics in `docs/RESEARCH.md` and `docs/algorithms/` over changes
that just happen to score well on the replay set with no clear causal
reason why.
