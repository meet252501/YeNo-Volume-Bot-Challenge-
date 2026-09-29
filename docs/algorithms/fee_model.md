# Fee Model — `src/fees.py`

Verified against real, current Polymarket documentation (see
`docs/RESEARCH.md` §1) — the brief's stated formula matches exactly.

## The two fee layers, both applied on entry AND exit

### Layer 1 — YeNo overlay
```python
YENO_OVERLAY_RATE = 0.01  # 1%, observed from YeNo test-account execution

def yeno_overlay_fee(notional_usd: float) -> float:
    return notional_usd * YENO_OVERLAY_RATE
```

### Layer 2 — Dynamic crypto taker fee (Polymarket-derived)
```python
CRYPTO_TAKER_RATE = 0.07  # confirmed against real Polymarket crypto feeRate

def taker_fee(shares: float, price: float) -> float:
    """fee = shares * feeRate * price * (1 - price) — peaks at price=0.50."""
    return shares * CRYPTO_TAKER_RATE * price * (1 - price)
```

### Combined round-trip cost estimate
```python
def round_trip_fee_estimate(entry_notional: float, entry_price: float,
                              exit_notional: float, exit_price: float,
                              shares: float) -> float:
    entry_fee = yeno_overlay_fee(entry_notional) + taker_fee(shares, entry_price)
    exit_fee = yeno_overlay_fee(exit_notional) + taker_fee(shares, exit_price)
    return entry_fee + exit_fee
```

## The strategic curve shape (from docs/RESEARCH.md §2)
Fee cost peaks at price=0.50 and falls toward zero at the extremes.
**A trade at 0.90 costs roughly a third of the same-size trade at 0.50.**
This is not a minor optimization — it's the single largest lever
available for preserving capital while still generating volume, since
it's structurally true regardless of directional skill.

## Worked example (from the brief itself, reproduce this exactly in tests)
- Gross BUY: $5.00
- Gross SELL: $4.91
- Credited toward $1,000 target after full exit: $9.91

This specific example should be a golden test case — if
`round_trip_fee_estimate` or the cycle accounting logic can't reproduce
this exact relationship, something is wrong before any strategy work
proceeds.

## What NOT to do
- Do not estimate fees with a flat percentage — the curve shape is the
  whole point; a flat estimate will misprice trades near 50¢ and near
  the extremes in opposite directions.
- Do not forget the fee applies on BOTH entry and exit — a strategy
  that only accounts for entry fees will systematically overestimate
  net proceeds.
