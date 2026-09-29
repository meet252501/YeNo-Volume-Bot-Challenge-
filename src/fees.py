"""
Fee model — both layers, verified against real Polymarket documentation.
See docs/algorithms/fee_model.md and docs/RESEARCH.md for the research
grounding these constants.
"""

from __future__ import annotations

YENO_OVERLAY_RATE = 0.01
CRYPTO_TAKER_RATE = 0.07


def yeno_overlay_fee(notional_usd: float) -> float:
    return notional_usd * YENO_OVERLAY_RATE


def taker_fee(shares: float, price: float) -> float:
    """fee = shares * feeRate * price * (1 - price) — peaks at price=0.50."""
    return shares * CRYPTO_TAKER_RATE * price * (1 - price)


def entry_or_exit_fee(notional_usd: float, shares: float, price: float) -> float:
    return yeno_overlay_fee(notional_usd) + taker_fee(shares, price)


def round_trip_fee_estimate(
    entry_notional: float,
    entry_price: float,
    entry_shares: float,
    exit_notional: float,
    exit_price: float,
    exit_shares: float,
) -> float:
    entry_fee = entry_or_exit_fee(entry_notional, entry_shares, entry_price)
    exit_fee = entry_or_exit_fee(exit_notional, exit_shares, exit_price)
    return entry_fee + exit_fee


def distance_from_mid(price: float) -> float:
    """Higher = further from 0.50 = cheaper fees + higher stated confidence."""
    return abs(price - 0.5)
