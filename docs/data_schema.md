# Data Schema — /decide Contract (working copy)

Reconstructed from the challenge page's published example. **Verify
against the real downloadable evaluator contract before treating this
as final** — this is a working transcription, not a fetched spec file.

## Request (evaluator → bot)

```json
{
  "market": { "id": "opaque", "secondsToClose": 84 },
  "account": { "cashUsd": 10, "eligibleVolumeUsd": 0, "position": null },
  "rules": {
    "maximumBuyCashUsd": 5,
    "targetVolumeUsd": 1000,
    "evaluationWindowHours": 24
  },
  "reference": {
    "btcMidUsd": 80482.155,
    "openingTargetUsd": 80444.946,
    "observedAt": 1789880823.619,
    "targetObservedAt": 1789880814.203,
    "targetProvisional": false
  },
  "books": {
    "YES": { "bids": [[0.49, 100]], "asks": [[0.50, 100]] },
    "NO":  { "bids": [[0.49, 100]], "asks": [[0.50, 100]] }
  }
}
```

### Field notes
- `market.secondsToClose` — countdown to market expiry. No new entries
  allowed once this drops under 15 seconds per the brief.
- `account.position` — `null` when flat; otherwise presumably an object
  describing the open position (shape not shown in the published
  example — confirm against the real contract before coding against it).
- `account.eligibleVolumeUsd` — running total toward the $1,000 target,
  presumably updated by the evaluator each call, not something the bot
  computes itself (though `src/cycle_tracker.py` should track its own
  copy for verification/backtesting purposes).
- `reference.observedAt` vs `reference.targetObservedAt` — two separate
  timestamps; `targetProvisional` flags whether the YeNo opening target
  itself might still be revised. Treat provisional targets with extra
  caution in any signal that depends on them.
- `books.YES` / `books.NO` — separate order books per outcome, each
  with `bids`/`asks` as `[price, size]` pairs.

## Response (bot → evaluator)

Exactly one of three shapes:

```json
{ "action": "HOLD" }
```
```json
{ "action": "BUY", "outcome": "YES", "maxCashUsd": 4.80 }
```
```json
{ "action": "SELL" }
```

### Field notes
- `BUY.maxCashUsd` — fee-inclusive ceiling; must never exceed $5 per
  the hard qualification rule. Build in a safety margin below $5.00
  exactly, don't rely on the fee calculation being exactly right to the
  cent under time pressure.
- `SELL` — requests a full exit. A partial fill on a SELL remains part
  of the same cycle, does not start a new one and does not require a
  second SELL call to "finish" it in terms of eligible-volume accounting
  (confirm this precisely against the real contract — the brief implies
  it but doesn't spell out the exact mechanics of a partially-filled SELL).

## Open questions to resolve against the real evaluator contract
- [ ] Exact shape of `account.position` when non-null
- [ ] Whether `HOLD` requires an empty object or no body at all
- [ ] Whether a malformed/invalid response is scored as an implicit HOLD
      or as a hard failure for that decision cycle
- [ ] Exact behavior when a BUY is requested but the book can't fill it
      at the requested price/size (rejected outright? partially filled
      at worse price? confirm before assuming either)
- [x] **RESOLVED (via competitor research, docs/competitor_repos.md):
      minimum order size is 5 shares.** A real competitor's local
      evaluator replica, built to match the published contract exactly,
      encodes a 5-share minimum. Not independently confirmed against
      Builderr's own contract directly, but a credible secondary
      source — verify against the real downloadable contract before
      fully trusting, but safe to design against in the meantime.
- [ ] **NEW, from competitor research:** whether `btcMidUsd` and
      `openingTargetUsd` come from the same underlying price feed —
      see `docs/algorithms/dual_feed_problem.md`
- [ ] **NEW, from competitor research:** exact settlement rule (working
      assumption: 60-second TWAP vs. 60-second pre-open TWAP, per
      `docs/algorithms/settlement_mechanics.md`) — this was derived from
      Polymarket resolution data, not confirmed directly against YeNo's
      own evaluator
