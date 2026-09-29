"""
Cycle accounting — complete-cycle-only eligible volume, matching the
evaluator's own accounting exactly. See docs/algorithms/cycle_accounting.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class CycleState(str, Enum):
    FLAT = "FLAT"
    OPENING = "OPENING"
    OPEN = "OPEN"
    CLOSING = "CLOSING"
    CLOSED = "CLOSED"


@dataclass
class Cycle:
    state: CycleState = CycleState.FLAT
    buy_notional_accum: float = 0.0
    sell_notional_accum: float = 0.0
    eligible_volume_contribution: float | None = None

    def record_buy_fill(self, notional: float, is_final_fill: bool = True) -> None:
        if self.state not in (CycleState.FLAT, CycleState.OPENING):
            raise ValueError(f"Cannot record BUY fill in state {self.state}")
        self.buy_notional_accum += notional
        self.state = CycleState.OPEN if is_final_fill else CycleState.OPENING

    def record_sell_fill(self, notional: float, is_final_fill: bool = True) -> None:
        if self.state not in (CycleState.OPEN, CycleState.CLOSING):
            raise ValueError(f"Cannot record SELL fill in state {self.state}")
        self.sell_notional_accum += notional
        if is_final_fill:
            self.state = CycleState.CLOSED
            self.eligible_volume_contribution = self.buy_notional_accum + self.sell_notional_accum
        else:
            self.state = CycleState.CLOSING

    @property
    def is_complete(self) -> bool:
        return self.state == CycleState.CLOSED

    @property
    def is_flat(self) -> bool:
        return self.state in (CycleState.FLAT, CycleState.CLOSED)


@dataclass
class CycleTracker:
    """Tracks eligible volume across a full run, one cycle at a time."""

    cycles: list[Cycle] = field(default_factory=list)
    current: Cycle = field(default_factory=Cycle)

    @property
    def total_eligible_volume(self) -> float:
        return sum(
            c.eligible_volume_contribution
            for c in self.cycles
            if c.eligible_volume_contribution is not None
        )

    @property
    def is_flat(self) -> bool:
        return self.current.is_flat

    def close_current_and_start_new(self) -> None:
        if not self.current.is_complete:
            raise ValueError("Cannot start a new cycle before the current one is CLOSED")
        self.cycles.append(self.current)
        self.current = Cycle()
