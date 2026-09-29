# Risk Management — `src/risk.py`

## Goal
Preserve capital while completing enough cycles to cross $1,000 in
eligible volume, and guarantee a flat ending — in that priority order,
since flat-by-deadline is a hard gate and ending cash is the primary
ranking metric.

## Position sizing
```python
SAFETY_MARGIN_USD = 0.15  # buffer below the hard $5.00 cap


def max_buy_size(remaining_cash: float) -> float:
    return min(5.00 - SAFETY_MARGIN_USD, remaining_cash)
```
The safety margin exists because fee computation happens on the
evaluator's side — a bot that always requests exactly $5.00 risks a
hard rejection if the evaluator's fee math rounds differently than the
bot's local estimate.

## The favorite-longshot haircut (from docs/RESEARCH.md §4)
Applied at decision time, not just documented as a note:
```python
def confidence_haircut(price: float) -> float:
    """Heavy favorites (>=0.85) resolve YES slightly less often than
    price implies, per documented academic findings. Apply a haircut
    rather than trusting the raw price as true probability."""
    if price >= 0.85 or price <= 0.15:
        return 0.03
    return 0.0
```

## Drawdown budget
Track running peak cash and current drawdown continuously. If drawdown
exceeds a conservative threshold (tune via backtest, start around 25%
of starting capital as a circuit-breaker default) with significant time
still remaining in the 24h window, shift to a more conservative
entry-scoring threshold rather than trying to "trade back" losses
aggressively — chasing losses under a hard deadline is how a bot ends
up unable to flatten in time.

## Flatten-by-deadline — the non-negotiable rule
```python
def must_flatten_now(seconds_remaining_in_run: float, position_open: bool) -> bool:
    SAFETY_BUFFER_S = 60  # never cut this margin too thin
    return position_open and seconds_remaining_in_run < SAFETY_BUFFER_S
```
This check overrides every other strategy consideration. A bot that's
in a slightly unfavorable position with 90 seconds left in the run
SELLS anyway — a marginally worse exit price costs far less than
disqualification for finishing non-flat.

## What NOT to do
- Do not size positions based only on account cash — also factor in how
  many more cycles are realistically needed to reach $1,000, so the bot
  doesn't run out of usable cash mid-window.
- Do not treat the drawdown circuit-breaker as optional — a bot that
  blows through its capital early has no path to recovery within a
  single 24h window with a $10 starting balance.
- Do not skip the flatten-by-deadline check "just this once" because a
  position looks likely to resolve favorably in the next few seconds —
  the rule is absolute, not probabilistic.
