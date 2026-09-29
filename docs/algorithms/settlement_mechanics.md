# Settlement Mechanics — How These Markets Actually Resolve

**This doc did not exist before this session's research pass. It covers
a gap in the original design: nothing previously modeled HOW a BTC
five-minute Up/Down market settles, only that it does.** This is the
single highest-value correction from `docs/RESEARCH.md` §7a — read that
section for full sourcing before treating this as settled fact.

## The finding (from a real competitor's out-of-sample-tested research)

Four candidate settlement definitions were tested against 2,014 real
Polymarket winners:

| Definition | Match rate |
|---|---|
| Last price vs. price at open | 87.3% |
| Last price 5s before close vs. open | 89.0% |
| Mean of the whole window vs. open | 84.1% |
| **Mean of the last 60s vs. mean of the 60s before open** | **98.0%** |

**Conclusion: this is a TWAP-style (time-weighted average price)
settlement over the final minute, compared against a TWAP over the
minute before open — not a last-price comparison.**

## Why this matters for entry/exit logic

A strategy that reacts to a late, sharp spike in the last few seconds
of a window is very likely **trading against the real settlement
rule**, not with it — a spike that doesn't hold for the full final
minute has limited effect on where the TWAP actually lands. This is
reported to have caused "most big losses" in an early version of the
competitor bot that didn't yet know this.

## Practical implication: the "projected settlement gap"

Rather than reacting to the instantaneous spot gap between current BTC
price and the opening target, a more settlement-aware signal is a
**projected gap**: the portion of the final-minute TWAP that's already
locked in (from elapsed seconds within that final minute) plus the
current price for the remaining seconds, compared against the opening
target. This requires the bot to maintain a short rolling history of
`reference.btcMidUsd` observations to reconstruct the partial TWAP —
it cannot be computed from a single point-in-time observation alone.

## Open items to verify before relying on this fully
- [ ] Confirm the exact settlement window (60s) and TWAP methodology
      against the real Builderr/YeNo evaluator documentation — this
      finding comes from testing against real Polymarket resolution
      data, and the challenge brief doesn't explicitly confirm YeNo's
      own BTC Up/Down markets use an identical rule, though it's a
      reasonable working assumption given the shared market structure
- [ ] Confirm whether the evaluator's own settlement uses the same
      60-second window, or a different one specific to this challenge

## What NOT to do
- Do not build any exit/entry logic that assumes last-price-at-close
  determines the outcome — per the 98.0% vs. 87.3% match rate gap,
  this is a measurably worse model of reality.
- Do not react to single-tick spikes late in a window as if they
  directly determine settlement — they only partially influence a
  60-second average.
