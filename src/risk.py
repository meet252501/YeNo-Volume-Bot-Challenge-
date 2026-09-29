"""
Risk management: sizing, favorite-longshot haircut, drawdown tracking,
flatten-by-deadline. See docs/algorithms/risk_management.md.
"""
from __future__ import annotations

from dataclasses import dataclass

SAFETY_MARGIN_USD = 0.15
HARD_BUY_CAP_USD = 5.00
FLATTEN_SAFETY_BUFFER_S = 60
DEFAULT_DRAWDOWN_BUDGET_PCT = 0.25  # of starting capital


def max_buy_size(remaining_cash: float) -> float:
    return max(0.0, min(HARD_BUY_CAP_USD - SAFETY_MARGIN_USD, remaining_cash))


def confidence_haircut(price: float) -> float:
    """
    Near the top of the tested-profitable band (see docs/RESEARCH.md
    §7b — real competitor data found entries above ~0.90 unprofitable),
    apply a haircut rather than trusting the raw price at face value.
    """
    if price >= 0.75:
        return 0.03
    return 0.0


MIN_ENTRY_PRICE = 0.30
MAX_ENTRY_PRICE = 0.80


def in_tested_profitable_band(price: float) -> bool:
    """
    Per docs/RESEARCH.md §7b: a real competitor's swept price-band data
    found 0.30-0.80 profitable, with entries above ~0.90 losing money
    on the week (fees ate the remaining upside). This is a correction
    from an earlier, unbounded "prefer the extremes" assumption.
    """
    return MIN_ENTRY_PRICE <= price <= MAX_ENTRY_PRICE


def must_flatten_now(seconds_remaining_in_run: float, position_open: bool) -> bool:
    return position_open and seconds_remaining_in_run < FLATTEN_SAFETY_BUFFER_S


@dataclass
class DrawdownTracker:
    starting_cash: float
    peak_cash: float | None = None

    def __post_init__(self):
        if self.peak_cash is None:
            self.peak_cash = self.starting_cash

    def update(self, current_cash: float) -> float:
        """Returns current drawdown as a fraction of starting cash."""
        self.peak_cash = max(self.peak_cash, current_cash)
        drawdown = self.peak_cash - current_cash
        return drawdown / self.starting_cash if self.starting_cash > 0 else 0.0

    def should_go_conservative(self, current_cash: float) -> bool:
        return self.update(current_cash) >= DEFAULT_DRAWDOWN_BUDGET_PCT
