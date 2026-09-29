# The Dual-Feed Problem — btcMidUsd vs. openingTargetUsd

New doc from this session's research pass — see `docs/RESEARCH.md` §7d
for sourcing. Not present in the original design.

## The risk

`reference.btcMidUsd` and `reference.openingTargetUsd` (see
`docs/data_schema.md`) may **not** come from the same underlying price
source. A real competitor's analysis found evidence consistent with one
being an exchange midpoint (e.g., ends in a half-cent, typical of a
bid/ask midpoint) and the other tracking a different, slower-updating
oracle-style feed (e.g., Chainlink, which was observed to print roughly
once a second and lag faster exchange feeds). The measured offset
between the two was real and non-trivial — roughly $10-30, and
**drifting over time**, not a fixed constant.

## Why this matters
Any signal that treats `btcMidUsd` and `openingTargetUsd` as directly
comparable — e.g., naively computing `btcMidUsd - openingTargetUsd` as
"the gap" — risks a systematic bias if the two numbers are on different
scales due to feed lag or methodology differences, not just genuine
price movement.

## A proposed mitigation (from the same source, not independently verified here)
Rather than assuming a fixed or zero offset, **read the offset from the
market itself**: at a moment when the order book is tight and roughly
balanced (e.g., near 0.50 on both sides), the true settlement gap
should be close to zero — so whatever `btcMidUsd - openingTargetUsd`
reads at that moment is, at least approximately, the feed offset itself
rather than genuine price movement. Taking a rolling median of several
such observations (the source used 40 samples) can track a slowly
drifting offset. Reported result: this method read offsets within
roughly $1-6 of independently-known true offsets in their test, most of
the time — with occasional larger misses (up to double digits) when the
underlying book briefly lagged a fast BTC move.

## What NOT to do
- Do not assume `btcMidUsd` and `openingTargetUsd` are the same feed
  without evidence — treat this as an open question to verify against
  the real evaluator contract before building a signal that depends on
  their difference being meaningful at face value.
- Do not hardcode a fixed offset constant — the drift observed in the
  source research means a static correction would go stale.

## Open items to verify against the real evaluator contract
- [ ] Confirm whether YeNo's evaluator actually uses two different
      underlying feeds for these two fields, or whether this concern
      is specific to the Polymarket-based research this finding came
      from and doesn't transfer directly
- [ ] If confirmed, decide whether the dynamic-offset-estimation
      approach above is worth implementing, or whether a simpler
      approach (e.g., ignoring small offsets below some threshold) is
      sufficient for this project's needs
