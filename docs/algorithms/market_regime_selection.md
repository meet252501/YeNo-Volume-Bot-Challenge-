# Market Regime Selection — When to Trade vs. Sit Out

## Goal
Not every 5-minute market window is worth entering. Sitting out a bad
setup costs nothing against the $1,000 target as long as there's still
time in the 24h window to make up the volume later — entering a bad
setup can cost real capital. This doc covers the "should I even look at
this market" layer, above the per-decision logic in `decision_algorithm.md`.

## Good setup signals (worth evaluating for entry)
- **Price within the tested-profitable band, roughly 0.30–0.80**
  (correction from `docs/RESEARCH.md` §7b — a real competitor's swept
  data found entries above ~0.90 lost money on the week; the fee-curve
  cheapness at the extremes doesn't translate into the best real
  profitability once the shrinking edge near the extremes is accounted
  for). Prefer distance from 0.50 as a tie-breaker *within* this band,
  not as an unbounded preference.
- Reasonable book depth at the touch — thin books mean the 250ms-later-book
  rule is more likely to produce a materially worse fill than expected
- Causal BTC reference signal aligned, accounting for the possible
  dual-feed offset (`docs/algorithms/dual_feed_problem.md`) — and
  `targetProvisional` is false, not true
- Late in the market's window (per `docs/algorithms/settlement_mechanics.md`,
  a real competitor's tested window was roughly 120s→20s before close,
  using a *projected* settlement gap rather than the raw spot gap) —
  balanced against the 15-second entry cutoff

## Bad setup signals (prefer HOLD)
- **Price outside the 0.30–0.80 band** — both near 0.50 (expensive fees,
  low edge) and above ~0.90 (fees eat the remaining upside per tested
  competitor data)
- `reference.targetProvisional` is true — the reference itself might
  still be revised
- Thin or one-sided book depth near expiry (explicitly called out in
  the execution model as a modeled condition, not a bug)
- Stale reference timestamps relative to `market.secondsToClose`

## Pacing across the 24-hour window
The bot doesn't need to fill every eligible window — it needs
**enough** complete cycles to reach $1,000. Rough math: at ~$9-10
credited per clean cycle (per the brief's own worked example), roughly
100-110 complete cycles are needed across 24 hours — a little over 4
per hour on average, not a maximum-frequency trading requirement.

**Implication:** there's no need to force a trade on a mediocre setup
just to "keep pace" early in the window — being selective early and
making up volume on genuinely good setups later is safer than accepting
worse setups purely to hit a self-imposed pacing target. Track actual
progress toward $1,000 against elapsed time, and only tighten selectivity
thresholds if genuinely falling behind pace with limited time left.

## What NOT to do
- Do not force trades to "stay on pace" if the pace math shows there's
  still comfortable time remaining — selectivity costs nothing but
  entering a bad setup costs real capital.
- Do not treat every 5-minute window as independent — the flatten
  deadline and pacing math operate on the full 24h run, not per-market.
