# Market Scope — YeNo BTC Five-Minute Up/Down

## What this market type is
A binary outcome market resolving every 5 minutes on whether BTC's
price is above (UP/YES) or below (DOWN/NO) a reference target set at
market open. Two independent order books exist per market instance —
one for YES, one for NO — per `docs/data_schema.md`'s `books` object.

## Why 5-minute windows specifically matter for this bot
- **High cadence** means many independent opportunities to complete
  cycles within the 24h window — this is structurally what makes the
  $1,000 target reachable at all from $10 of capital reused repeatedly.
- **Short time-to-resolution** means less exposure per position — a
  bad entry can't compound losses over hours the way a longer-duration
  market could.
- **Near-expiry pricing tends toward the extremes** as the outcome
  becomes clearer — this is very likely *why* the fee curve's
  cheap-near-extremes shape (`docs/RESEARCH.md` §2) and the "trade near
  expiry" pattern in the included House Bot v1 go together naturally:
  waiting until a window is nearly resolved often means trading at a
  cheaper, more confident price point, not just a more certain one.

## What's genuinely uncertain about this market type (flag before assuming)
- Exact resolution mechanics (how "the price at close" is determined,
  whether there's any dispute/oracle-delay period) — not detailed in
  the challenge brief as captured; check the real evaluator contract
- Whether multiple 5-minute market instances can be "seen" (offered via
  `/decide` calls) concurrently, or whether the evaluator only ever
  presents one active market at a time to the bot — this materially
  affects whether `market_regime_selection.md`'s pacing math needs to
  account for parallel opportunities or purely sequential ones
