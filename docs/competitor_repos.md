# Competitor & Reference Repos Found via Research

Found via web search this session — real, existing repos relevant to
this challenge or its underlying market type. Credibility varies
significantly; noted per entry.

## Direct competitor for this exact challenge

### `github.com/AnSa30-06/yeno-late-favourite` — HIGH credibility
The primary source behind most of this session's research updates (see
`docs/RESEARCH.md` §7, `docs/algorithms/settlement_mechanics.md`,
`docs/algorithms/dual_feed_problem.md`). A real `/decide` bot submission
for this exact challenge, single-file (`bot.py`), stdlib-only, with:
- Out-of-sample methodology: strategy tuned on 3 days, tested untouched
  on 4 different days
- Whole-day replay across 7 real recorded days with 1¢/2¢ adverse
  slippage stress — **crossed $1,000 in 7 of 7 full-day replays at 1¢
  slippage**, 7 of 7 at 2¢
- Live L2 order-book recording and replay through a local evaluator
  that reproduces the real contract's mechanics
- Three rounds of documented adversarial code review with specific
  bugs found and fixed (listed in their README)
- Explicit, honest "what this evidence does not prove" section —
  flags real caveats (settlement feed uncertainty, rebuilt vs. real
  depth, small live sample size) rather than overclaiming

**Why this is worth reading in full, not just summarized here:** the
settlement-mechanics finding (§7a) and price-band correction (§7b)
came directly from this repo's own documented research process, not
from this project's own testing. Read their actual README before
finalizing any entry/exit strategy — this summary necessarily loses
detail.

**What NOT to do with this repo:** do not copy `bot.py` directly as a
submission — that would not be this project's own work, and more
importantly its parameters were tuned on specific historical data that
may not transfer perfectly to the real unseen evaluation window. Use
it as a research reference and a methodology benchmark, not a
copy-paste source.

## Adjacent strategy research (same underlying market type, different platform/challenge)

### `github.com/Duclos76/confidence-surfing-bot` — MEDIUM credibility
A Polymarket trading bot (not built for this Builderr challenge
specifically) targeting the same general market type: 5-minute and
15-minute Up/Down crypto markets, across XRP/BNB/ETH/SOL/BTC/DOGE.
Documents a **momentum-confirmation strategy**: enter when one side is
priced ≥0.70 (crowd has formed a strong view) and a live price feed
confirms that view — explicitly framed as "not a contrarian or
arbitrage strategy." Worth knowing as an alternative strategy family
that exists and is documented publicly, though it wasn't evaluated
with anywhere near Late-Favourite's rigor (no out-of-sample testing
described, no whole-day replay results shown in what was found).
Interesting as a contrast: this strategy actively trades the price
range (≥0.70) that Late-Favourite's own tested data found became
unprofitable above ~0.90 due to fees — the two approaches may be
targeting different parts of the same underlying edge, or one may
simply be less rigorously validated. Don't treat as equally trustworthy
without independently checking its claims.

### `github.com/Benjam1nCup/Polymarket-trading-bot-python-V2` — LOW credibility, reference only
A broader "framework" repo listing many named strategies (sniper,
ladder, stair, momentum, copy trading) for Polymarket's short-duration
crypto markets. Reads more like a marketing aggregator than a
rigorously documented research project (promotional language, demo
video links, no methodology or backtest evidence found in what was
retrieved). Useful only as a vocabulary/taxonomy reference for strategy
family names that exist in this space — not as a source of validated
claims.

## Explicitly excluded — flagged as unreliable, not cited as research

### `github.com/randomaccountgit` (multiple repos)
Several repos targeting this same market type (e.g.
"bitcoin-market-timing-system", "bitcoin-5min-pattern-recognition")
repeat the **identical phrase "87% accuracy verified" / "87% prediction
accuracy" word-for-word across otherwise-unrelated project
descriptions**. This is a strong, specific red flag for templated
marketing copy rather than independently verified results — a real
backtest result for a "pattern recognition" project and a "market
timing" project landing on the exact same round number, phrased
identically, is not a coincidence worth trusting. **Excluded from this
project's research basis entirely** — noted here only so a future
research pass doesn't waste time re-discovering and re-evaluating the
same repos.

## What to do with this catalog going forward
- If time allows, read `yeno-late-favourite`'s actual `bot.py` and
  `tests/test_bot.py` in full (not just the README) before finalizing
  `src/decision.py` — there may be implementation details (their depth
  checks, their state-reconciliation approach) worth learning from
  beyond what the README summarizes.
- Do not treat any single competitor's tuned parameters (their specific
  0.30-0.80 band, their specific 120s-20s window) as necessarily
  optimal for this project's own bot — they were tuned on their own
  training data; re-derive or at least re-validate against this
  project's own replay data once available.
