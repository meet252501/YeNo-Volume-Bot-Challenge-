"""
Tests for src/cycle_tracker.py, including the brief's own worked
example: $5.00 gross BUY, $4.91 gross SELL -> $9.91 credited.
"""
import pytest

from src.cycle_tracker import Cycle, CycleState, CycleTracker


def test_worked_example_from_brief():
    """The brief's own numbers — must reproduce exactly."""
    cycle = Cycle()
    cycle.record_buy_fill(notional=5.00)
    cycle.record_sell_fill(notional=4.91, is_final_fill=True)
    assert cycle.is_complete
    assert cycle.eligible_volume_contribution == pytest.approx(9.91)


def test_incomplete_cycle_contributes_nothing():
    cycle = Cycle()
    cycle.record_buy_fill(notional=5.00)
    assert not cycle.is_complete
    assert cycle.eligible_volume_contribution is None


def test_partial_fills_accumulate_in_same_cycle():
    cycle = Cycle()
    cycle.record_buy_fill(notional=2.50, is_final_fill=False)
    assert cycle.state == CycleState.OPENING
    cycle.record_buy_fill(notional=2.50, is_final_fill=True)
    assert cycle.state == CycleState.OPEN
    assert cycle.buy_notional_accum == pytest.approx(5.00)

    cycle.record_sell_fill(notional=2.00, is_final_fill=False)
    assert cycle.state == CycleState.CLOSING
    assert cycle.eligible_volume_contribution is None  # not credited yet
    cycle.record_sell_fill(notional=2.91, is_final_fill=True)
    assert cycle.is_complete
    assert cycle.eligible_volume_contribution == pytest.approx(9.91)


def test_cannot_start_new_cycle_before_current_is_closed():
    tracker = CycleTracker()
    tracker.current.record_buy_fill(notional=5.00)
    with pytest.raises(ValueError):
        tracker.close_current_and_start_new()


def test_tracker_accumulates_across_multiple_cycles():
    tracker = CycleTracker()
    tracker.current.record_buy_fill(notional=5.00)
    tracker.current.record_sell_fill(notional=4.91)
    tracker.close_current_and_start_new()

    tracker.current.record_buy_fill(notional=3.00)
    tracker.current.record_sell_fill(notional=2.95)
    tracker.close_current_and_start_new()

    assert tracker.total_eligible_volume == pytest.approx(9.91 + 5.95)
    assert tracker.is_flat
