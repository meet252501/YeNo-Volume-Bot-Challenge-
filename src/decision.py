"""
Core decision logic: HOLD / BUY / SELL. Pure function of request state
+ internal tracker state -> decision. See docs/algorithms/decision_algorithm.md.
"""
from __future__ import annotations

from src.cycle_tracker import CycleTracker
from src.fees import distance_from_mid
from src.models import BuyAction, DecideRequest, DecideResponse, HoldAction, SellAction
from src.risk import confidence_haircut, in_tested_profitable_band, max_buy_size, must_flatten_now

STALE_BOOK_THRESHOLD_S = 2.0
ENTRY_CUTOFF_S = 15.0
MIN_ENTRY_CONFIDENCE = 0.15  # tune via backtest; distance-from-mid threshold


def validate_state(request: DecideRequest, now: float) -> str | None:
    """Returns a reason to force HOLD, or None if free to proceed."""
    book_age = now - request.reference.observedAt
    if book_age > STALE_BOOK_THRESHOLD_S:
        return "stale_book"
    if request.market.secondsToClose < ENTRY_CUTOFF_S and request.account.position is None:
        return "entry_cutoff"
    return None


def entry_score(price: float, causal_signal_aligned: bool) -> float:
    """
    Per docs/RESEARCH.md §7b (correction from an earlier, unbounded
    "prefer the extremes" assumption): real competitor data found
    0.30-0.80 profitable, entries above ~0.90 losing money on the week
    because fees ate the remaining upside. Gate on the band first.
    """
    if not in_tested_profitable_band(price):
        return 0.0
    confidence = distance_from_mid(price) - confidence_haircut(price)
    if not causal_signal_aligned:
        confidence *= 0.5
    return confidence


def causal_signal_aligned(request: DecideRequest, outcome_price: float) -> bool:
    """
    Cheap directional check: does the causal BTC reference agree with
    the cheaper/more-confident side implied by the book? Placeholder
    logic — refine against real replay data, and never trust a
    provisional target the same as a confirmed one.
    """
    if request.reference.targetProvisional:
        return False
    up_signal = request.reference.btcMidUsd > request.reference.openingTargetUsd
    yes_is_cheap_side = outcome_price < 0.5
    return up_signal == (not yes_is_cheap_side)


def decide(request: DecideRequest, tracker: CycleTracker, now: float,
           seconds_remaining_in_run: float) -> DecideResponse:
    """
    Main entry point. Pure given (request, tracker state, now,
    seconds_remaining_in_run) — no hidden global state.
    """
    # Step 0: flatten-by-deadline overrides everything else
    if must_flatten_now(seconds_remaining_in_run, position_open=not tracker.is_flat):
        return SellAction()

    # Step 1: state validation always runs first
    hold_reason = validate_state(request, now)
    if hold_reason is not None:
        return HoldAction()

    # Step 2: already holding a position -> exit logic
    if request.account.position is not None:
        # Simple baseline: exit whenever we're free to act and not forced
        # to hold by staleness/cutoff (cutoff doesn't block SELL, only BUY).
        return SellAction()

    # Step 3: flat and free to act -> evaluate entry
    yes_ask = request.books.YES.asks[0][0] if request.books.YES.asks else None
    no_ask = request.books.NO.asks[0][0] if request.books.NO.asks else None
    if yes_ask is None and no_ask is None:
        return HoldAction()

    candidates = []
    if yes_ask is not None:
        candidates.append(("YES", yes_ask))
    if no_ask is not None:
        candidates.append(("NO", no_ask))

    best_outcome, best_price = max(
        candidates,
        key=lambda oc: entry_score(oc[1], causal_signal_aligned(request, oc[1])),
    )
    score = entry_score(best_price, causal_signal_aligned(request, best_price))

    if score < MIN_ENTRY_CONFIDENCE:
        return HoldAction()

    size = max_buy_size(request.account.cashUsd)
    if size <= 0:
        return HoldAction()

    return BuyAction(outcome=best_outcome, maxCashUsd=round(size, 2))
