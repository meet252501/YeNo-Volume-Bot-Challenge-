# Architecture

## Pipeline overview (text diagram)

```
                    ┌────────────────────────────┐
                    │  Evaluator: POST /decide      │
                    │  (market, account, rules,       │
                    │   reference, books)               │
                    └──────────────┬─────────────┘
                                       │
                                       ▼
                    ┌────────────────────────────┐
                    │  1. STATE VALIDATION            │
                    │  book freshness (<2s), position   │
                    │  count, cash remaining, time-to-    │
                    │  close vs. entry cutoff (15s)         │
                    └──────────────┬─────────────┘
                                       │
                                       ▼
                    ┌────────────────────────────┐
                    │  2. REGIME / SIGNAL SCORING      │
                    │  distance-from-0.5, causal BTC       │
                    │  reference alignment, book depth,      │
                    │  spread quality                          │
                    └──────────────┬─────────────┘
                                       │
                                       ▼
                    ┌────────────────────────────┐
                    │  3. FEE-AWARE EXPECTED VALUE      │
                    │  project both fee layers on entry    │
                    │  AND exit before ever committing        │
                    └──────────────┬─────────────┘
                                       │
                                       ▼
                    ┌────────────────────────────┐
                    │  4. RISK / SIZING GATE              │
                    │  position cap ($5), drawdown          │
                    │  budget, cycles-remaining-in-window     │
                    └──────────────┬─────────────┘
                                       │
                                       ▼
                    ┌────────────────────────────┐
                    │  5. DECISION: HOLD/BUY/SELL         │
                    │  return exactly one action              │
                    └──────────────┬─────────────┘
                                       │
                                       ▼
                    ┌────────────────────────────┐
                    │  6. CYCLE / STATE TRACKING          │
                    │  reconcile fills, track eligible        │
                    │  volume, flatten-by-deadline logic        │
                    └────────────────────────────┘
```

## Component responsibilities

### `src/models.py`
Pydantic models for the exact `/decide` request/response shape. Single
source of truth for the contract — everything else imports from here,
never hand-parses raw dicts.

### `src/fees.py`
Pure functions implementing both fee layers exactly: the 1% YeNo
overlay and the `0.07 × shares × price × (1-price)` dynamic taker fee
(verified against real Polymarket documentation — see `docs/RESEARCH.md`).
Every expected-value calculation anywhere else in the codebase must
route through this module — never re-derive fee math inline elsewhere.

### `src/decision.py`
The actual `HOLD` / `BUY` / `SELL` logic. Pure function of
(request state, internal risk state) → decision. No hidden global
state — must produce the same decision given the same inputs, since
the real evaluator may call this fresh each time.

### `src/risk.py`
Position sizing, drawdown tracking, and the "haircut" applied to
near-certain prices per the favorite-longshot bias finding in
`docs/RESEARCH.md`. Also owns the flatten-by-deadline logic — this is
a hard qualification requirement, not a nice-to-have.

### `src/cycle_tracker.py`
Tracks BUY→SELL cycles exactly per `docs/algorithms/cycle_accounting.md`
— partial fills stay in the same cycle, incomplete cycles never count
toward eligible volume. This is the module most likely to have subtle
bugs that quietly cost real points; it has the heaviest test coverage.

### `src/api/server.py`
FastAPI implementation of `POST /decide`, used for local testing and
as the reference implementation for what an HTTPS-endpoint submission
would look like. Not required if submitting via repository/commit
instead of a live endpoint — check which submission mode Builderr
actually expects before assuming this needs to be deployed anywhere.

### `src/backtest/`
Replay harness — runs the decision function against
`data/replay/*.json` paths and produces a report matching the shape
Builderr's own benchmark used (median, best, worst, flat-rate %,
stressed-execution numbers).

## Design principles
1. **Fee-aware by construction.** No decision is made without first
   projecting the full round-trip fee cost — this is the central
   constraint per the research findings, not an afterthought.
2. **Fail closed on ambiguity.** A timeout is not permission to retry
   blindly (per the brief's own "treat writes as ambiguous" rule) —
   always reconcile actual venue state before acting again.
3. **Flat-by-deadline is non-negotiable.** This is checked with the
   same seriousness as the $1,000 target itself — a bot that reaches
   $1,000 but ends with an open position doesn't qualify at all.
4. **No component assumes live network access during evaluation** — the
   evaluator blocks arbitrary outbound network; every input the bot
   needs must come through the `/decide` request itself.
