# Starter Kit Variant Analysis

Per the challenge page, three reference configurations are published.
Working analysis based on the page's own description — verify against
the real downloadable source before treating this as authoritative.

## House Bot v1 — $559 median / $943 best (18/30 flat)
Trades five-share BTC-reference moves near expiry, checks immediate
exit depth, caps entry loss, allows two cycles per market. This is the
**baseline every change should be measured against** per
`docs/learning_harness.md` — reproduce it first, beat it second.

## Precision variant — $169 median / $762 best
Requires the order book to agree with the public BTC signal and aims
for a small positive exit; trades less often. **Lower median but a
high best-case** suggests this variant is more selective (fewer
trades, higher quality per trade) — consistent with
`docs/algorithms/market_regime_selection.md`'s "don't force trades on
mediocre setups" principle, but its much lower median suggests it may
be *too* conservative, missing enough cycles to reliably reach volume
targets even when individual trades are sound.

## Aggressive reference variant — $168 median / $818 best
Same signal family without the immediate-loss cap. Per the page's own
description: "found more upside in some paths but was less reliable."
**Lower median than even the precision variant** despite being
"aggressive" — suggests removing the loss cap increases variance
without a corresponding improvement in typical-case performance. Worth
treating as a cautionary reference: raw aggressiveness without the
fee-curve-aware selectivity from `docs/RESEARCH.md` doesn't obviously help.

## What this comparison suggests
The house bot's combination of *some* selectivity (immediate-loss cap)
with *reasonable* trade frequency (two cycles per market, not zero, not
unlimited) outperforms both a more conservative and a more aggressive
variant on median performance. This is weak evidence, not proof, that
the right direction is "smarter selectivity" (per the fee-curve and
favorite-longshot research) rather than simply "more trades" or "fewer,
higher-conviction trades" alone.
