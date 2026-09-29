# Extended Glossary — Fee & Execution Terms

Supplements `docs/glossary.md` with terms specific to the fee/execution
research (see `docs/RESEARCH.md`).

- **Taker fee** — a fee paid by the side of a trade that removes
  liquidity from the book (crosses an existing order), as opposed to a
  **maker**, who adds liquidity and typically pays zero fee. This
  challenge's evaluator models taker-only fees, per real Polymarket policy.
- **feeRate** — the category-specific multiplier in the fee formula;
  0.07 for crypto markets specifically (other Polymarket categories use
  different rates, not relevant here since this challenge is BTC-only).
- **L2 order book** — a "level 2" book showing price levels and
  aggregated size at each level (as opposed to L1, which shows only the
  best bid/ask), or L3, which shows individual orders. The `books`
  object in `docs/data_schema.md` is effectively L2-shaped
  (`[price, size]` pairs).
- **Slippage** — the difference between the price a trader expects and
  the price they actually get filled at, typically due to the order
  consuming multiple price levels or the market moving between decision
  and execution (directly relevant here given the 250ms later-book rule).
- **Wash trading** — placing trades with no genuine economic purpose
  other than to inflate volume, often by trading against oneself or a
  coordinated party. Explicitly forbidden by this challenge's
  qualification rules and a live regulatory concern (see
  `docs/RESEARCH.md` §5) — relevant context, not something this bot's
  design needs to actively defend against beyond simply not doing it.
- **Circuit breaker** — an automatic rule that shifts a system to a more
  conservative mode once a risk threshold is crossed; used here for the
  drawdown budget (`src/risk.py::DrawdownTracker`).
