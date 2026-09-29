# Glossary

- **Eligible volume** — executed BUY notional + executed SELL notional,
  counted only for complete cycles; the metric the $1,000 target is
  measured against.
- **Cycle** — one full BUY→SELL round trip on a single position. Partial
  fills on either side stay within the same cycle.
- **Flat** — zero open positions and zero pending actions. Required at
  the end of the 24h run regardless of whether $1,000 was reached.
- **Taker fee** — the dynamic crypto fee (`0.07 × shares × price ×
  (1-price)`), paid on both entry and exit; peaks at a 50¢ price.
- **YeNo overlay** — the additional flat 1% fee layer specific to this
  challenge's paper-trading account, on top of the taker fee.
- **Later book** — the order-book state the evaluator actually fills
  against, taken 250ms after the bot's decision, not the book the bot
  observed when deciding.
- **Provisional target** — a YeNo opening-target reference value flagged
  as possibly still subject to revision (`targetProvisional: true`).
- **Flatten-by-deadline** — the rule requiring zero open positions when
  the 24h evaluation window ends, independent of per-market timers.
- **Favorite-longshot bias** — the documented tendency for heavily
  favored contracts (price ≥0.85) to resolve as the favored outcome
  slightly less often than the price implies.
