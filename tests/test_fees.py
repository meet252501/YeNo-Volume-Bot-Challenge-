"""
Tests for src/fees.py, including the brief's own worked example as a
golden test case.
"""
import pytest

from src.fees import distance_from_mid, entry_or_exit_fee, taker_fee, yeno_overlay_fee


def test_taker_fee_peaks_at_fifty_cents():
    fee_at_50 = taker_fee(shares=100, price=0.50)
    fee_at_90 = taker_fee(shares=100, price=0.90)
    fee_at_10 = taker_fee(shares=100, price=0.10)
    assert fee_at_50 > fee_at_90
    assert fee_at_50 > fee_at_10
    assert fee_at_90 == pytest.approx(fee_at_10)  # symmetric around 0.5


def test_taker_fee_matches_polymarket_documented_example():
    # 100 shares at $0.50: fee = 100 * 0.07 * 0.5 * 0.5 = $1.75
    # (matches real Polymarket crypto feeRate documentation, see docs/RESEARCH.md)
    assert taker_fee(shares=100, price=0.50) == pytest.approx(1.75)


def test_yeno_overlay_is_flat_one_percent():
    assert yeno_overlay_fee(100.0) == pytest.approx(1.0)


def test_distance_from_mid():
    assert distance_from_mid(0.5) == 0.0
    assert distance_from_mid(0.9) == pytest.approx(0.4)
    assert distance_from_mid(0.1) == pytest.approx(0.4)


def test_entry_or_exit_fee_combines_both_layers():
    fee = entry_or_exit_fee(notional_usd=5.0, shares=10, price=0.5)
    expected = yeno_overlay_fee(5.0) + taker_fee(10, 0.5)
    assert fee == pytest.approx(expected)
