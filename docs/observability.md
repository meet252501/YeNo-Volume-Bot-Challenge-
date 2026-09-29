# Observability During a 24-Hour Run

## Why this matters more than it might seem
A bug that only manifests after 6+ hours of runtime (a slow state leak,
a rare edge case in book parsing, an accumulating rounding error in fee
estimates) could silently ruin an otherwise-good run — and with only
one official 24h evaluation window, there's no opportunity to notice
and fix it mid-run the way there would be during iterative backtesting.

## What to log, every single decision cycle
- Timestamp, market ID, action taken (HOLD/BUY/SELL), and the reasoning
  score that led to it (entry_score value, or the flatten-by-deadline
  trigger, or the staleness/cutoff HOLD reason)
- Running totals: eligible volume so far, current cash, current
  drawdown, cycles completed
- Any state-reconciliation event (a timeout followed by a state check)
  — these are exactly the moments a subtle bug is most likely to hide

## What to alert on (even in a "fire and forget" 24h run)
- Drawdown crossing the circuit-breaker threshold
- A reconciliation mismatch between expected and evaluator-reported state
- Any exception in the decision path — this must never crash the
  process; catch, log, and fail safe (HOLD, or SELL if a position is
  open and time is short) rather than let an unhandled exception risk
  a non-flat ending

## Post-run analysis
After every backtest AND (once running for real) every actual
evaluation window, produce the same `ReplayReport`-shaped summary (see
`src/backtest/report.py`) so real results are directly comparable to
backtest expectations — a large gap between backtested and real
results is itself an important signal that the backtest harness is
missing something about real execution conditions.
