"""Tests for src/risk.py."""

import pytest

from src.risk import (
    DrawdownTracker,
    confidence_haircut,
    max_buy_size,
    must_flatten_now,
)


def test_max_buy_size_respects_hard_cap_with_margin():
    assert max_buy_size(remaining_cash=100) == pytest.approx(4.85)  # 5.00 - 0.15


def test_max_buy_size_respects_low_remaining_cash():
    assert max_buy_size(remaining_cash=2.00) == pytest.approx(2.00)


def test_max_buy_size_never_negative():
    assert max_buy_size(remaining_cash=0) == 0.0


def test_confidence_haircut_applies_near_band_top():
    """Updated per docs/RESEARCH.md §7b correction — band is 0.30-0.80,
    haircut applies near the top of the tested-profitable band, not at
    both raw extremes as originally (incorrectly) assumed."""
    assert confidence_haircut(0.80) == pytest.approx(0.03)
    assert confidence_haircut(0.75) == pytest.approx(0.03)
    assert confidence_haircut(0.50) == 0.0
    assert confidence_haircut(0.30) == 0.0


def test_must_flatten_now_triggers_within_buffer():
    assert must_flatten_now(seconds_remaining_in_run=30, position_open=True) is True
    assert must_flatten_now(seconds_remaining_in_run=120, position_open=True) is False
    assert must_flatten_now(seconds_remaining_in_run=10, position_open=False) is False


def test_drawdown_tracker_flags_conservative_mode():
    tracker = DrawdownTracker(starting_cash=10.0)
    assert tracker.should_go_conservative(current_cash=10.0) is False
    assert tracker.should_go_conservative(current_cash=7.0) is True  # 30% drawdown > 25% budget


def test_in_tested_profitable_band():
    """Per docs/RESEARCH.md §7b: real competitor data found 0.30-0.80
    profitable, entries above ~0.90 lost money on the week."""
    from src.risk import in_tested_profitable_band

    assert in_tested_profitable_band(0.50) is True
    assert in_tested_profitable_band(0.30) is True
    assert in_tested_profitable_band(0.80) is True
    assert in_tested_profitable_band(0.20) is False
    assert in_tested_profitable_band(0.90) is False
