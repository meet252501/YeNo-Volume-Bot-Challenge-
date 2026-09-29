# Challenge Brief Summary — YeNo Volume Bots / Builderr.ai

Condensed from the Builderr.ai challenge page (sponsored by YeNo).
Working summary — cross-check against the real downloadable evaluator
contract before building anything submission-critical.

## Basics
- Platform: Builderr.ai, sponsored by YeNo
- Challenge: Global bot challenge — free to enter, rolling qualification
  (no fixed close date published on the page as captured)
- Prize: $500 first prize + possible additional YeNo rewards or pilot
  opportunities under separate written terms
- Format: code-only submission, paper-traded by Builderr against real
  YeNo BTC market data — no real funds, no real account, ever

## The task
Start with $10 simulated cash. Generate at least $1,000 in completed
trading volume within a 24-hour official evaluation window, while
losing as little as possible to fees/spreads/bad exits, and finish
with zero open positions.

## Hard qualification rules (all must hold)
1. Evaluator starts with exactly $10 — no top-ups, no leverage, no
   borrowing
2. No single BUY may spend more than $5 cash, fees included
3. At least $1,000 in eligible executed volume within the 24h run
4. Must finish flat — zero positions, zero pending actions (no separate
   minimum ending-balance rule beyond this)
5. At most one open position or pending BUY at a time
6. YeNo BTC five-minute Up/Down markets only
7. Must return valid decisions and reproduce exactly from the submitted
   immutable commit or container digest
8. Never self-trade, coordinate fills, or trade against another
   competition bot or entrant-controlled account

## What counts as "eligible volume"
`executed BUY notional + executed SELL notional`, counted only for
**complete cycles**. Explicitly worth **zero**: rejected orders,
cancellations, zero fills, settlements/redemptions, pending inventory,
and incomplete exits. Partial fills combine into the same cycle rather
than each counting separately.

Worked example from the brief: $5.00 gross BUY, $4.91 gross SELL →
$9.91 credited toward the $1,000 target after the full exit completes.

## Ranking (in order — later tiers only break ties)
1. **Primary:** highest ending simulated cash, among bots that both
   reached $1,000 and finished flat, at the first clean crossing of
   the target
2. **Tiebreak 1:** lower maximum peak-to-trough drawdown wins
3. **Tiebreak 2:** faster time to reach $1,000 wins

## Execution realism the evaluator models (this is the hard part)
- **Two fee layers, both applied on entry and exit:** a 1% YeNo overlay
  (observed from their test account) plus a dynamic crypto taker fee of
  `0.07 × shares × price × (1 − price)` — modeled on Polymarket's
  published fee mechanics (crypto rate, price-curve shape, taker-only
  application, five-decimal precision)
- **250ms decision-to-fill delay**, crossing a *later* L2 order-book
  update for the chosen outcome — a bot cannot act on a quote it already
  observed; an opposite-side update can't be reused either
- **Partial fills are real:** displayed depth, minimum order size, split
  exits, share dust, and executable one-sided books near expiry are all
  modeled. A partial exit stays part of the same cycle, doesn't reset it
- **Writes are ambiguous on timeout** — a timeout is not permission to
  retry blindly; the bot must reconcile the venue's actual state first
  or risk accidentally opening a duplicate position
- **Book staleness rejected:** quotes older than 2 seconds are rejected
  outright
- **Hard entry cutoff:** no new entries allowed in the final 15 seconds
  of a market; the account must be completely flat when the 24h window
  ends
- **Reference data is causal-only:** the request may include a public
  BTC midpoint, the YeNo opening target, receive timestamps, and a
  provisional flag — future-stamped target rows are excluded, so the
  bot can never see data from "the future" relative to its decision point

## Market scope
BTC five-minute Up/Down markets only. Official qualification uses one
**unseen**, receive-time-ordered 24-hour YeNo window — the published
replay/benchmark data is for development only, not the scoring run.

## Interface contract (see docs/data_schema.md for full detail)
`POST /decide` — JSON in, JSON out. Bot returns exactly one of:
`HOLD`, `BUY {outcome: YES|NO, maxCashUsd}`, or `SELL` (full-exit
request; partial fills remain one cycle).

## Submission mechanics
Submit a repository or HTTPS endpoint, plus an immutable commit hash or
container digest. Official runs block arbitrary outbound network access
and record the exact input-data hash used — the bot cannot assume any
live network call succeeds during the real evaluation.

## The published development benchmark (honest, not promotional)
As of the Sep 22, 2026 snapshot on the challenge page: across 30
resampled development replay paths, the house bot (the one included in
the starter kit) achieved a **$559 median**, **$943 best** — and
**never once crossed $1,000**. 18 of 30 paths finished flat; median
among flat paths was $680. Under a 2-cent adverse-execution stress test,
the best run fell to $385 and the median to $70. The page states this
plainly: **"No validation path crossed $1,000."** This is a real,
current, unsolved-as-published problem — not a template with a known
answer to copy.

## Starter kit contents (per the challenge page)
- House Bot v1 — five-share BTC-reference moves near expiry, checks
  immediate exit depth, caps entry loss, allows two cycles per market
  ($559 median / $943 best)
- Precision variant — requires order book to agree with the public BTC
  signal, aims for small positive exit, trades less often
  ($169 median / $762 best)
- Aggressive reference variant — same signal family, no immediate-loss
  cap; more upside on some paths, less reliable overall
  ($168 median / $818 best)
- Evaluator contract, tested configurations, full source download
