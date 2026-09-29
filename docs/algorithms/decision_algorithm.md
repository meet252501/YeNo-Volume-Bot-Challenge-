# Decision Algorithm — `src/decision.py`

## Goal
Given the current `/decide` request, return exactly one of HOLD, BUY,
or SELL — maximizing ending cash subject to: crossing $1,000 eligible
volume, finishing flat, never exceeding $5/BUY, at most one open
position at a time.

## Step 1 — Always validate state first, before any strategy logic
```python
def validate_state(request) -> str | None:
    """Returns a reason to force HOLD, or None if free to proceed."""
    if request.reference.observedAt_age_seconds > 2:
        return "stale_book"
    if request.market.secondsToClose < 15 and request.account.position is None:
        return "entry_cutoff"  # can still SELL an existing position, just can't BUY
    if request.account.position is not None and request.account.pending_action:
        return "pending_action_exists"
    return None
```
This must run before anything else. A HOLD returned here is not a
missed opportunity — it's the evaluator's own rule being respected.

## Step 2 — If flat and free to act: score the entry opportunity
Per `docs/RESEARCH.md` §2-3 and §7b (**correction applied**), distance
from 0.50 is a real fee-cost signal, but real tested data from a
competitor's out-of-sample research shows profitability does NOT keep
improving all the way to the extremes — their swept price band found
**0.30-0.80 profitable, with entries above ~0.90 actually losing money**
because fees ate the remaining upside. Score for a bounded sweet spot,
not "more extreme is always better":

```python
def entry_score(price: float, book_depth: float, causal_signal_aligned: bool) -> float:
    # Bounded band, not monotonic distance-from-mid — see docs/RESEARCH.md §7b
    PRICE_BAND_LOW, PRICE_BAND_HIGH = 0.30, 0.80
    if not (PRICE_BAND_LOW <= price <= PRICE_BAND_HIGH):
        return 0.0  # outside the tested-profitable band — do not enter

    distance_from_mid = abs(price - 0.5)  # still a real tie-breaker within the band
    # Favorite-longshot haircut (docs/RESEARCH.md §4): don't trust the
    # raw price as true probability near the upper edge of the band.
    haircut = 0.03 if price >= 0.75 else 0.0
    confidence = distance_from_mid - haircut
    if not causal_signal_aligned:
        confidence *= 0.5  # reference signal disagrees — be more cautious
    return confidence
```

## Step 3 — Fee-aware expected value gate
Never commit to a BUY without projecting the FULL round-trip cost
(entry fee + assumed exit fee) via `src/fees.py`. Reject any entry
whose projected round-trip fee cost, relative to the position size,
would need an unrealistically large favorable move to recover.

## Step 4 — Sizing
Position size ≤ `min($5.00 - safety_margin, remaining_cash)`. Safety
margin exists because the fee calculation happens in the evaluator, not
just locally — don't submit a BUY at exactly $5.00 and hope the fee
math matches to the cent.

## Step 5 — If holding a position: exit logic
- If a clean profitable exit is available at current book depth, SELL.
- If time-to-close is approaching zero and the position is still open,
  SELL regardless of price — flat-by-deadline is a hard gate, worth
  more than a marginally better exit price.
- Never let "waiting for a better price" risk missing the flatten
  deadline.

## What NOT to do
- Do not chase multiple simultaneous signals across different markets —
  the "at most one open position at a time" rule means this is a
  sequential, not parallel, strategy by construction.
- Do not treat a near-certain price as a guaranteed win (see the
  favorite-longshot bias finding) — always apply the haircut.
- Do not retry a BUY/SELL after a timeout without first checking actual
  account state — see `docs/algorithms/execution_model.md`.
