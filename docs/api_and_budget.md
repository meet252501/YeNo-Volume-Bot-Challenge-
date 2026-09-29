# Timing & Resource Notes

Unlike the Signalpost project, this challenge has no explicit dollar
API-cost budget — it's free to enter and the bot never touches real
money or a real API bill. The equivalent constraints here are timing
and correctness, not cost:

## Timing constraints to respect
- 250ms decision-to-fill delay is fixed by the evaluator, not
  something the bot controls — no advantage to responding faster than
  whatever the real timeout is (unconfirmed exact value — check the
  real evaluator contract)
- Books older than 2 seconds are rejected — the bot's own decision
  latency should stay comfortably under this
- 24-hour total evaluation window — pacing math in
  `docs/algorithms/market_regime_selection.md` targets roughly 100-110
  complete cycles across the full window, not a burst at the start

## Reliability constraints
- The bot must handle a full 24h run without crashing or hanging — a
  single unhandled exception mid-run could mean failing to flatten by
  deadline, which is a hard disqualification
- No outbound network access during official runs — every dependency
  the decision function needs must be computed locally from the
  request payload alone
