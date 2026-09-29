# Cycle Accounting — `src/cycle_tracker.py`

## Goal
Track eligible volume exactly the way the evaluator will score it, so
local backtest numbers are trustworthy and the bot never assumes credit
for volume that wouldn't actually count.

## What counts (from the brief, verbatim)
`executed BUY notional + executed SELL notional`, for **complete
cycles only**.

## What scores zero, explicitly
- Rejected orders
- Cancellations
- Zero fills
- Settlements/redemptions
- Pending inventory (an open, unresolved position)
- Incomplete exits

## Cycle state machine
```
FLAT
  │  BUY submitted, first fill received
  ▼
OPENING (partial fills accumulate here, not yet "complete")
  │  cumulative filled shares == requested shares
  ▼
OPEN (fully filled position, eligible volume NOT yet credited)
  │  SELL submitted, first fill received
  ▼
CLOSING (partial exit fills accumulate here)
  │  cumulative sold shares == position shares
  ▼
CLOSED → credit (BUY notional + SELL notional) to eligible volume, return to FLAT
```

**Critical implementation detail:** eligible volume is credited only at
the CLOSED transition — never incrementally during OPENING or CLOSING.
A bot that credits volume on the BUY alone (before the position is ever
sold) would overstate its own backtest numbers relative to what the
real evaluator counts.

## Worked example (matches the brief's own numbers — golden test case)
```python
def test_worked_example():
    cycle = Cycle()
    cycle.record_buy_fill(notional=5.00)
    cycle.record_sell_fill(notional=4.91, is_final_fill=True)
    assert cycle.is_complete
    assert cycle.eligible_volume_contribution == pytest.approx(9.91)
```

## Partial fill handling
```python
class Cycle:
    def record_buy_fill(self, notional: float, is_final_fill: bool = True):
        self.buy_notional_accum += notional
        self.state = "OPEN" if is_final_fill else "OPENING"

    def record_sell_fill(self, notional: float, is_final_fill: bool = True):
        self.sell_notional_accum += notional
        if is_final_fill:
            self.state = "CLOSED"
            self.eligible_volume_contribution = (
                self.buy_notional_accum + self.sell_notional_accum
            )
        else:
            self.state = "CLOSING"
```

## What NOT to do
- Do not credit eligible volume before a cycle is fully CLOSED.
- Do not start a new cycle while a previous one is still OPENING/OPEN/
  CLOSING — this would also violate the "at most one open position at a
  time" hard rule, not just the accounting.
- Do not assume a SELL request results in an immediate, single, complete
  fill — always handle the CLOSING partial-fill path, since the
  execution model explicitly says partial exits are real and expected.
