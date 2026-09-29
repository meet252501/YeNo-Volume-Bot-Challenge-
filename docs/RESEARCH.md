# Research Synthesis — Pre-Build Research

Written 2026-09-25, concluding the research phase before implementation.
Every claim below was checked with a live search on this date. Sources
linked inline. This grounds the algorithm docs in real market mechanics
rather than guesswork.

## 1. The fee formula in the brief is real, current Polymarket policy — verified

The brief states: *"dynamic crypto taker fee, 0.07 × shares × price ×
(1 − price)."* This is confirmed, exactly, against Polymarket's own
current fee documentation (docs.polymarket.com/trading/fees): fee =
`C × feeRate × p × (1-p)`, with the **crypto category's feeRate at
0.07** — one of several 2026 sources independently confirming the same
number (crypticorn.com, predictionhunt.com, kairos.trade). This fee was
introduced on Polymarket's short-duration (15-minute) crypto markets
specifically, without a formal announcement, and — notably —
**one CoinMarketCap analysis frames the change as a deliberate anti-bot,
anti-wash-trading measure**, not a general revenue policy: *"characterized
... as a market structure adjustment that targets wash trading and
high-frequency bot activity."*

**Why this matters for this project specifically:** the fee curve this
bot has to navigate was likely designed, at least partly, to make
exactly this kind of volume-generating bot activity expensive. That's
not a reason not to build it (YeNo is explicitly sponsoring and
requesting it) — but it explains why the house bot's own benchmark
never crosses $1,000, and it means fee-curve awareness isn't optional,
it's the central design constraint.

## 2. The fee curve shape has a direct, exploitable strategic implication

Because `p × (1-p)` peaks at p=0.5 and falls to zero at the extremes,
**dollar fees are highest on a coin-flip market and lowest on a
near-certain one.** Multiple sources confirm the concrete numbers: a
100-share crypto trade at 50¢ costs ~$1.75 in fees (7.2% effective
rate at the worst point); the same trade at 90¢ costs roughly $0.63
(a third as much).

**Direct implication for this bot:** trading near-certain, late-stage
markets isn't just lower-risk directionally — it is *structurally
cheaper per dollar of volume generated*, because the fee curve itself
rewards trading away from 50/50. This is very likely *why* the
included House Bot v1 already trades "near expiry" — it's not just
chasing directional confidence, it's also minimizing the fee tax. Any
strategy revision should treat "how close to 0 or 1 is the price at
entry" as a first-class cost variable, not just a confidence signal.

## 3. A real, documented pattern matches this exact goal: "Resolution Sniper"

A production prediction-market bot toolkit (HarrierOnChain, GitHub,
2026) documents a named strategy directly analogous to what this
challenge wants:

> *"Resolution Sniper — Scan for near-certainty contracts (e.g. 95¢+)
> where the market has effectively resolved but hasn't paid out, and
> hold to $1.00. High win-rate, low per-trade return — it compounds on
> volume, not on swings."*

This is close to a direct blueprint for the "preserve capital while
generating volume" goal: small, high-confidence, high-win-rate cycles
repeated many times, rather than a few large directional bets. The
same source also documents an "Orderbook Imbalance" signal (near-touch
bid/ask depth skew as a short-term directional read, refreshed every
500ms) — relevant given this challenge's own 250ms decision cadence.

## 4. A real, cited academic finding: near-certainty isn't actual certainty

A 2026 academic paper (arXiv, *"The Favorite-Longshot Bias in
Prediction Markets: Evidence from Polymarket"*) documents that
contracts priced as heavy favorites (YES ≥ 0.85) **resolve as YES
slightly less often than their price implies** — a real, measured bias,
not a theoretical curiosity.

**Implication:** a "trade near-certain markets" strategy (per §2-3
above) cannot assume a 95¢ price means a 95% win rate in practice — it
may be modestly worse. Risk management (`docs/algorithms/risk_management.md`)
should build in a margin for this, not assume the displayed price is a
perfectly calibrated probability.

## 5. A live regulatory signal, worth knowing even though it doesn't change what to build

A CFTC staff advisory (Letter 26-23, referenced via ZeroHedge's Aug 2026
coverage of a Kalshi wash-trading dispute) explicitly warns that
*"volume-based rewards with steep tiers or threshold bonuses can
encourage participants to trade solely to reach volume targets,
heightening risks of wash trading."* This is the exact risk category
this challenge type sits inside, industry-wide, right now — which is
almost certainly why the qualification rules explicitly forbid
self-trading and coordinated fills against other entrant-controlled
accounts. Not something to design around technically, just useful
context for why those specific rules exist and why they're likely to
be strictly enforced.

## 6. A real methodological pattern worth copying for the backtest harness

An open-source Kalshi paper-trading bot (simonziervogel/trading-bot,
GitHub) draws a methodologically important distinction: **hold-to-expiry
strategies get a full historical backtest with statistical significance
testing (Wilson confidence intervals)**, while **path-dependent,
take-profit/stop-loss strategies are only validated live via paper
trading**, because low-resolution candle data "can't reliably simulate
an intra-candle TP/SL fill" — and the author explicitly states that
pretending to backtest them anyway "would overstate confidence."

**Direct implication for `docs/algorithms/backtesting_algorithm.md`:**
if this bot's strategy ever becomes path-dependent (e.g., an in-flight
stop-loss based on live order-book movement rather than a fixed
hold-to-resolution rule), the replay-based backtest numbers for that
part of the strategy should be treated with real skepticism, not
reported with the same confidence as a hold-to-expiry rule's backtest.

## 7. A real competitor repo exists for this exact challenge — and its findings correct part of this document

Found via web search: **`github.com/AnSa30-06/yeno-late-favourite`** ("Late-Favourite"), a public
submission for this exact YeNo × Builderr challenge, with unusually rigorous methodology —
out-of-sample testing (rules tuned on 3 days, tested untouched on 4 unseen days), whole-day replay
across 7 real recorded days with adverse-slippage stress, live L2 book recording, and three rounds
of documented adversarial code review. This is the single most valuable source found this session
and materially changes two things this project's docs previously got wrong or left unaddressed.

### 7a. How these markets actually settle — previously undocumented here, and important

Late-Favourite tested four candidate settlement definitions against **2,014 real Polymarket
winners** (7 days of data):

| Settlement definition | Matches the real winner |
|---|---|
| last price vs. price at open | 87.3% |
| last price 5s before close vs. open | 89.0% |
| mean of the whole window vs. open | 84.1% |
| **mean of the last 60s vs. mean of the 60s before open** | **98.0%** |

**This means these are TWAP-style (time-weighted average) settlements, not last-price settlements.**
A bot that reacts to a late spike in the final few seconds is very likely trading against the real
settlement rule, not with it — Late-Favourite's own account says exactly this caused "most big
losses in the first version of this bot." This is a materially important correction: nothing
elsewhere in this project's docs previously modeled settlement as anything other than an
unspecified black box. See the new `docs/algorithms/settlement_mechanics.md`.

### 7b. The price-band guidance in this document needs a correction

§2-3 above argued, correctly as far as the fee-curve math goes, that fees are cheapest near the
price extremes (0 or 1). Late-Favourite's real tested data shows this is **only true up to a
point**: their swept price band was **0.30–0.80**, and they found entries **above ~0.90 actually
lost money on the week** because — in their words — "fees eat the rest of the upside." Below 0.50
was their most profitable region, because "the book has not caught up with BTC yet."

**Correction:** the fee curve being cheapest at the extremes does not mean the extremes are the
most *profitable* place to enter — the edge (how mispriced the book is relative to true probability)
also shrinks near the extremes, since there's less room left for the price to move favorably. The
right way to read this is: prefer distance from 0.50 as a tie-breaker and a real cost saving, but
don't chase prices near 0.90+ expecting them to be better — Late-Favourite's real, tested data says
the opposite happened in their case. `docs/algorithms/decision_algorithm.md` and
`market_regime_selection.md` have been updated to reflect a bounded band, not "more extreme is
always better."

### 7c. A concrete, causal reason for late-window entries — refines rather than replaces this doc's earlier reasoning

Late-Favourite's own explanation for *why* the late-window favourite edge exists: "the side the
BTC reference favours is priced below its real chance of winning" in the final part of the window.
Their large-sample measurement: on 226 recorded Polymarket markets (345,766 trades), favourites
bought 30–60s before close with a $20–50 settlement gap traded around 0.86 and won about 96% of
the time — while entries earlier (60–90s) *lost* about $0.58 per $5 cycle after fees. Their final
bot design widened this to a 120s→20s entry window using the *projected* settlement gap (see
§7a) rather than the raw spot gap, which measurably improved results in their own out-of-sample test.

### 7d. Two different BTC reference feeds may be in play — a real, previously unconsidered risk

Late-Favourite's evidence: `reference.btcMidUsd` and `reference.openingTargetUsd` may come from
**different underlying price feeds** (e.g., an exchange midpoint vs. Chainlink), which run a real,
drifting offset from each other (their measurement: roughly $10-30, drifting over time, occasionally
spiking much higher). If a bot's strategy assumes both numbers are directly comparable without
accounting for this, its signal could be systematically biased. See the new
`docs/algorithms/dual_feed_problem.md` for their proposed mitigation (reading the offset from the
market itself rather than assuming a fixed value).

### 7e. Head-to-head evidence against the house bot, on the same real data
On an 11-minute live-recorded-book test, Late-Favourite completed 2 cycles for **+$0.98**, while
**House Bot v1 lost −$1.75 on the same books**. Small sample, explicitly flagged by its own author
as not conclusive — but it's a genuine, real, same-data comparison, not a simulated claim.

### 7f. Related but less rigorous / less trustworthy sources found — flagged, not relied upon
A GitHub account (`randomaccountgit`) hosts several repos ("bitcoin-market-timing-system",
"bitcoin-5min-pattern-recognition") targeting this same general market type, but multiple of their
repo descriptions repeat the **identical phrase "87% accuracy verified" / "87% prediction accuracy"
word-for-word across unrelated projects** — a strong signal of templated marketing copy, not
independently verified results. Excluded from this project's research basis; noted here only so a
future search doesn't waste time re-evaluating them as if they were credible.

A separate, more general "confidence-surfing-bot" repo (Duclos76) documents a **momentum-confirmation
strategy family** for the same underlying Polymarket 5-min/15-min Up/Down market type: entering
when one side is priced ≥0.70 and a live price feed confirms the crowd's view, rather than betting
on a settlement-mechanics mispricing. Worth knowing as an alternative strategy family that exists in
the wild, though it wasn't evaluated with the same rigor as Late-Favourite's out-of-sample testing.

## Recommendations (updated, prioritized)

1. **Model settlement as a TWAP over the final 60 seconds vs. the 60 seconds before open**, not a
   last-price comparison — see §7a and the new `docs/algorithms/settlement_mechanics.md`. This is
   the single highest-value correction from this session's research.
2. **Use a bounded price band (roughly 0.30-0.80) for entries, not "prefer the extremes without
   limit"** — see §7b. Update entry scoring to reflect a sweet spot, not a monotonic preference for
   distance-from-0.50.
3. **Treat `btcMidUsd` and `openingTargetUsd` as potentially different feeds with a real, driftable
   offset** — do not assume they're directly comparable without a dynamic offset correction. See
   `docs/algorithms/dual_feed_problem.md`.
4. **Adopt the out-of-sample testing discipline demonstrated by Late-Favourite**: tune on a subset
   of days, validate untouched on a different subset, before trusting any strategy change. This is
   a stronger standard than this project's own `docs/learning_harness.md` currently requires —
   worth tightening that doc to match.
5. Everything from the original recommendations (§1-6, now renumbered as historical context above)
   still holds as directionally correct — the fee-curve-awareness and favorite-longshot-haircut
   findings are not contradicted, just refined by more specific, real, tested data.

## Sources consulted this session (original + this update)
- Polymarket Fees documentation — https://docs.polymarket.com/trading/fees
- "Polymarket Introduces Taker-Only Fees on 15-Minute Crypto Bets" — CoinMarketCap, Jan 2026
- "Polymarket Fees Explained" — KuCoin, Mar 2026; startpolymarket.com; crypticorn.com, Aug 2026; kairos.trade, Jul 2026
- HarrierOnChain Prediction-Markets-Trading-Bot-Toolkits — GitHub
- "The Favorite-Longshot Bias in Prediction Markets: Evidence from Polymarket" — arXiv, 2609.12878
- simonziervogel/trading-bot — GitHub (Kalshi paper-trading bot, backtest methodology)
- ZeroHedge, "Kalshi's $5,499 Question: Wash Trading, Or A Subsidized Volume Machine?" — Aug 2026 (CFTC Letter 26-23 reference)
- "Most prediction market contracts have low volume..." — CNBC, Jul 2026
- "Prediction Markets Are Turning Into a Bot Playground" — Finance Magnates
- **AnSa30-06/yeno-late-favourite — GitHub (primary new source this update; direct competitor repo for this exact challenge)**
- yeno.market / yeno.trade — YeNo's own site (confirms real Solana-settled BTC/ETH Up/Down markets exist as a live product, separate from this paper-trading challenge)
- Duclos76/confidence-surfing-bot — GitHub (alternative momentum-confirmation strategy family, lower confidence)
- randomaccountgit — GitHub (multiple repos found but excluded as unreliable; templated/duplicated accuracy claims across unrelated projects)
