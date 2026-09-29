# Edge Case Catalog

Test each of these explicitly — do not rely on the general replay run
to exercise all of them, since some are rare enough that they may not
appear in every replay path.

## Book/data edge cases
- [ ] Empty order book on one or both sides (no bids or no asks)
- [ ] Book exactly at the 2-second staleness boundary (off-by-one risk)
- [ ] `targetProvisional: true` on a market the bot would otherwise enter
- [ ] `secondsToClose` exactly at the 15-second entry-cutoff boundary

## Position/cycle edge cases
- [ ] A BUY that receives only a partial fill, then no further fills
      arrive before the market resolves (stuck partial position)
- [ ] A SELL that receives only a partial fill near the flatten deadline
      — must the bot re-request SELL for the remainder, or does the
      evaluator handle this automatically? (open question — see
      `docs/data_schema.md`)
- [ ] Two consecutive HOLD-forcing conditions in a row (e.g., stale book
      immediately followed by entry cutoff) — confirm no state corruption

## Timing edge cases
- [ ] Run start-of-window and end-of-window boundary behavior — first
      and last few minutes of the 24h run
- [ ] A position still open when wall-clock time in the run crosses the
      flatten-safety-buffer threshold mid-market (not at a market's own
      close, but the outer 24h deadline)

## Financial edge cases
- [ ] Cash balance too low to make the minimum viable BUY (confirm
      minimum order size from the real evaluator contract — not
      specified in the working brief)
- [ ] A fee estimate that would push a BUY over the $5.00 cap if not
      for the safety margin — confirm the margin is sufficient across
      the full price range, not just near 0.50
