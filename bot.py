#!/usr/bin/env python3
"""
YeNo x Builderr Volume Bot — "Velocity" v2

A Late-Favourite bot for YeNo BTC five-minute Up/Down markets.
Starts with $10 simulated cash, targets $1,000+ completed volume in 24h.

Strategy summary (grounded in competitor research, docs/RESEARCH.md):
──────────────────────────────────────────────────────────────────────
1. SETTLEMENT MODEL — TWAP-style resolution (98% match vs 87% for last-
   price). We track a rolling BTC reference window and project the
   settlement gap using partial TWAP, not raw spot difference.

2. ENTRY TIMING — 120s → 16s before market close. Competitor data shows
   favourites bought 30-60s before close at a $20-50 gap won ~96% of
   the time. We use a wide window with pacing-based adaptive thresholds.

3. FEE CURVE EXPLOITATION — The p*(1-p) taker fee means trading at
   p=0.90 costs ~1/3 of trading at p=0.50. But competitor data shows
   entries ABOVE 0.90 actually lose money (fees eat remaining upside).
   We target the 0.20-0.88 band, preferring sub-0.50 (book lag).

4. DUAL FEED OFFSET — btcMidUsd and openingTargetUsd may be different
   feeds (exchange mid vs Chainlink oracle) with $10-30 drifting offset.
   We estimate and correct for this using balanced-book observations.

5. PACING — At ~$9.50 per clean cycle, we need ~105 cycles in 24h out
   of ~288 possible markets (37% hit rate). When behind pace, thresholds
   relax; when ahead, we stay selective.

6. MINIMUM 5 SHARES — Confirmed from competitor's evaluator replica.

7. IMMEDIATE EXIT CHECK — Before committing to BUY, project the full
   round-trip (entry fees + exit fees) and reject if immediate exit
   loss exceeds threshold.

Evidence class: development code. Not yet validated against replay data.
The house bot's best was $943. The competitor's yeno-late-favourite
crossed $1,000 in 7/7 full-day replays at 1c slippage.
"""

from __future__ import annotations

import json
import math
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


# ═══════════════════════════════════════════════════════════════════════
# ORDER BOOK HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _levels(rows: Any, *, reverse: bool) -> list[tuple[float, float]]:
    """Parse L2 rows into sorted (price, size) tuples."""
    output: list[tuple[float, float]] = []
    for row in rows if isinstance(rows, list) else []:
        try:
            price, size = float(row[0]), float(row[1])
        except (IndexError, TypeError, ValueError):
            continue
        if 0 < price < 1 and size > 0:
            output.append((price, size))
    return sorted(output, reverse=reverse)


def _best_bid(bids_raw: Any) -> float | None:
    """Get best bid price, or None if no bids."""
    lvls = _levels(bids_raw, reverse=True)
    return lvls[0][0] if lvls else None


def _best_ask(asks_raw: Any) -> float | None:
    """Get best ask price, or None if no asks."""
    lvls = _levels(asks_raw, reverse=False)
    return lvls[0][0] if lvls else None


def _total_depth(rows: Any) -> float:
    """Total available size across all levels."""
    return sum(size for _, size in _levels(rows, reverse=False))


# ═══════════════════════════════════════════════════════════════════════
# FEE MODEL — verified against real Polymarket docs (RESEARCH.md §1)
# Two layers: 1% YeNo overlay + 0.07 * shares * p * (1-p) taker fee
# Both applied on entry AND exit.
# ═══════════════════════════════════════════════════════════════════════

def _fees_for_fills(fills: list[tuple[float, float]]) -> float:
    """Compute total fees (both layers) for a set of (price, shares) fills."""
    gross = sum(price * shares for price, shares in fills)
    # Polymarket taker fee: 0.07 * shares * price * (1 - price)
    # Rounded to 5 decimal places per Polymarket docs
    protocol = sum(0.07 * shares * price * (1 - price) for price, shares in fills)
    # YeNo 1% overlay on gross notional
    overlay = gross * 0.01
    return round(protocol + 1e-12, 5) + round(overlay + 1e-12, 5)


def _walk_asks(asks_raw: Any, target_shares: float) -> tuple[float, float, list[tuple[float, float]]] | None:
    """Walk the ask side to buy `target_shares`.
    Returns (gross_cost, fees, fills) or None if insufficient depth."""
    remaining = target_shares
    fills: list[tuple[float, float]] = []
    for price, available in _levels(asks_raw, reverse=False):
        qty = min(remaining, available)
        fills.append((price, qty))
        remaining -= qty
        if remaining <= 1e-9:
            break
    if remaining > 1e-9:
        return None
    gross = sum(p * q for p, q in fills)
    fees = _fees_for_fills(fills)
    return gross, fees, fills


def _walk_bids(bids_raw: Any, target_shares: float) -> tuple[float, float, list[tuple[float, float]]] | None:
    """Walk the bid side to sell `target_shares`.
    Returns (gross_proceeds, fees, fills) or None if insufficient depth."""
    remaining = target_shares
    fills: list[tuple[float, float]] = []
    for price, available in _levels(bids_raw, reverse=True):
        qty = min(remaining, available)
        fills.append((price, qty))
        remaining -= qty
        if remaining <= 1e-9:
            break
    if remaining > 1e-9:
        return None
    gross = sum(p * q for p, q in fills)
    fees = _fees_for_fills(fills)
    return gross, fees, fills


# ═══════════════════════════════════════════════════════════════════════
# TWAP TRACKER — Settlement is TWAP over final 60s vs 60s before open
# (98% match rate, vs 87% for last-price — RESEARCH.md §7a)
# ═══════════════════════════════════════════════════════════════════════

class TWAPTracker:
    """Rolling window of BTC mid observations for TWAP settlement projection."""

    def __init__(self, window_seconds: float = 70.0) -> None:
        self.window = window_seconds
        self.obs: deque[tuple[float, float]] = deque()  # (timestamp, btc_mid)

    def update(self, timestamp: float, btc_mid: float) -> None:
        self.obs.append((timestamp, btc_mid))
        cutoff = timestamp - self.window
        while self.obs and self.obs[0][0] < cutoff:
            self.obs.popleft()

    def twap(self, now: float, lookback_s: float = 60.0) -> float | None:
        """Time-weighted average price over last `lookback_s` seconds."""
        if len(self.obs) < 1:
            return None
        cutoff = now - lookback_s
        pts = [(t, p) for t, p in self.obs if t >= cutoff]
        if not pts:
            return self.obs[-1][1] if self.obs else None
        if len(pts) == 1:
            return pts[0][1]
        weighted_sum = 0.0
        total_dt = 0.0
        for i in range(len(pts) - 1):
            dt = pts[i + 1][0] - pts[i][0]
            if dt > 0:
                weighted_sum += pts[i][1] * dt
                total_dt += dt
        # Extend last observation to now
        tail_dt = now - pts[-1][0]
        if tail_dt > 0:
            weighted_sum += pts[-1][1] * tail_dt
            total_dt += tail_dt
        return weighted_sum / total_dt if total_dt > 1e-9 else pts[-1][1]


# ═══════════════════════════════════════════════════════════════════════
# DUAL FEED OFFSET ESTIMATOR (RESEARCH.md §7d)
# btcMidUsd vs openingTargetUsd may be different underlying feeds
# with a $10-30 drifting offset.
# ═══════════════════════════════════════════════════════════════════════

class OffsetEstimator:
    """Estimates feed offset when book is balanced (near 0.50)."""

    def __init__(self, max_samples: int = 40) -> None:
        self.samples: deque[float] = deque(maxlen=max_samples)

    def maybe_record(self, btc_mid: float, target: float,
                     yes_ask: float | None, no_ask: float | None) -> None:
        if yes_ask is not None and no_ask is not None:
            if 0.44 <= yes_ask <= 0.56 and 0.44 <= no_ask <= 0.56:
                self.samples.append(btc_mid - target)

    @property
    def offset(self) -> float:
        if len(self.samples) < 3:
            return 0.0
        s = sorted(self.samples)
        return s[len(s) // 2]


# ═══════════════════════════════════════════════════════════════════════
# THE BOT
# ═══════════════════════════════════════════════════════════════════════

class VelocityBot:
    """
    Adaptive late-favourite volume bot.

    Identifies near-certain late-window BTC prediction markets where the
    TWAP-projected settlement gap strongly favours one outcome, buys shares
    at fee-optimal prices, and exits quickly for a small profit or
    controlled loss. Repeats ~105 cycles in 24h to cross $1,000 volume.
    """

    # ── CORE PARAMETERS ──────────────────────────────────────────────
    # These are the primary levers. Grounded in competitor research
    # (yeno-late-favourite), house bot benchmarks, and fee curve analysis.

    # Minimum order size (confirmed from competitor evaluator replica)
    MIN_SHARES = 5.0

    # Default trade size
    TARGET_SHARES = 5.0

    # Entry window: enter between ENTRY_WINDOW_S and ENTRY_CUTOFF_S
    # before market close. Competitor data: 120s->20s optimal.
    ENTRY_WINDOW_S = 130.0
    ENTRY_CUTOFF_S = 16.0  # evaluator blocks at 15s; 1s safety margin

    # Forced exit: sell open positions before this many seconds to close
    FORCED_EXIT_S = 50.0

    # Price band (RESEARCH.md §7b): 0.30-0.80 tested profitable by
    # competitor. Below 0.50 was MOST profitable ("book hasn't caught up").
    # Above ~0.90 lost money. We widen slightly for more opportunities.
    MIN_ENTRY_PRICE = 0.18
    MAX_ENTRY_PRICE = 0.88

    # BTC gap thresholds
    # Competitor data: $20-50 gap at 30-60s before close = 96% win rate
    MIN_GAP_USD = 15.0        # base minimum gap
    STRONG_GAP_USD = 40.0     # gap considered "strong signal"

    # Reference data freshness
    MAX_REFERENCE_AGE_S = 2.0

    # Risk per trade
    MAX_IMMEDIATE_LOSS_USD = 0.45   # reject entries with worse round-trip
    STOP_LOSS_PER_SHARE = 0.09      # per-share stop loss
    TAKE_PROFIT_THRESHOLD = -0.015  # exit when PnL >= this (near break-even)

    # Per-market limits
    MAX_CYCLES_PER_MARKET = 4
    REENTRY_COOLDOWN_S = 1.0

    # Sizing
    BUY_CAP_USD = 5.00
    SAFETY_MARGIN_USD = 0.12  # below $5 cap for fee math mismatch

    # Pacing
    TARGET_VOLUME = 1000.0
    VOLUME_PER_CYCLE = 9.5  # ~$5 buy + ~$4.50 sell
    EVAL_HOURS = 24.0

    def __init__(self) -> None:
        # Per-market state
        self.market_id: str | None = None
        self.position_was_open = False
        self.completed_cycles = 0
        self.last_flat_at = -math.inf
        self.last_buy_attempt_at = -math.inf

        # Cross-market state
        self.run_start: float | None = None
        self.twap = TWAPTracker()
        self.offset_est = OffsetEstimator()

        # Track volume for pacing (cross-checked with evaluator's number)
        self.local_volume = 0.0

    # ── MAIN ENTRY POINT ─────────────────────────────────────────────

    def decide(self, obs: dict[str, Any]) -> dict[str, Any]:
        try:
            return self._decide(obs)
        except (KeyError, TypeError, ValueError, OverflowError,
                ZeroDivisionError, IndexError):
            return {"action": "HOLD"}

    def _decide(self, obs: dict[str, Any]) -> dict[str, Any]:
        # ── Parse ──
        market = obs["market"]
        account = obs["account"]
        books = obs["books"]
        rules = obs.get("rules", {})
        now = float(obs.get("timestamp", time.time()))
        ttc = float(market["secondsToClose"])         # time to close
        mid = str(market["id"])
        position = account.get("position")
        cash = float(account["cashUsd"])
        volume = float(account.get("eligibleVolumeUsd", 0))

        # Init run clock
        if self.run_start is None:
            self.run_start = now

        self.local_volume = volume

        # ── Market reset ──
        if mid != self.market_id:
            self.market_id = mid
            self.position_was_open = False
            self.completed_cycles = 0
            self.last_flat_at = -math.inf
            self.last_buy_attempt_at = -math.inf

        # ── Track cycles ──
        if position is None and self.position_was_open:
            self.completed_cycles += 1
            self.last_flat_at = now
        self.position_was_open = position is not None

        # ── Feed updates ──
        ref = obs.get("reference")
        ref_valid = (isinstance(ref, dict)
                     and not bool(ref.get("targetProvisional", True)))

        if ref_valid:
            btc = float(ref["btcMidUsd"])
            target = float(ref["openingTargetUsd"])
            obs_at = float(ref.get("observedAt", 0))

            if btc > 0 and obs_at > 0:
                self.twap.update(obs_at, btc)

            # Record offset when book is balanced
            ya = _best_ask(books.get("YES", {}).get("asks", []))
            na = _best_ask(books.get("NO", {}).get("asks", []))
            if btc > 0 and target > 0:
                self.offset_est.maybe_record(btc, target, ya, na)

        # ── Pacing ──
        elapsed_h = (now - self.run_start) / 3600.0
        remaining_h = max(0.01, self.EVAL_HOURS - elapsed_h)
        vol_left = max(0.0, self.TARGET_VOLUME - volume)
        cycles_needed = vol_left / self.VOLUME_PER_CYCLE
        cycles_per_hr_needed = cycles_needed / remaining_h
        # Urgency: >1.0 means behind pace (comfortable is ~4.5/hr)
        urgency = min(4.0, cycles_per_hr_needed / 4.5)

        # Already crossed target? Stay selective to preserve cash
        past_target = volume >= self.TARGET_VOLUME

        # ═══════════════════════════════════════════════════════════════
        # SELL LOGIC (holding a position)
        # ═══════════════════════════════════════════════════════════════
        if position is not None:
            side = str(position["outcome"])
            shares = float(position["shares"])
            side_bids = books.get(side, {}).get("bids", [])

            # Can we execute?
            sell_result = _walk_bids(side_bids, shares)

            # Forced exit near market close OR near end of 24h run
            seconds_remaining_in_run = (self.EVAL_HOURS * 3600.0) - (now - self.run_start)
            if ttc <= self.FORCED_EXIT_S + 1e-9 or seconds_remaining_in_run <= 60.0:
                return {"action": "SELL"}

            if sell_result is None:
                # Can't fill — hold and wait for depth
                return {"action": "HOLD"}

            sell_gross, sell_fees, _ = sell_result

            # Calculate full-cycle P&L
            # We must gracefully handle different possible evaluator schemas for the position
            if "notional_paid" in position:
                paid = float(position["notional_paid"])
            else:
                paid = (float(position.get("buy_gross_usd", 0))
                        + float(position.get("buy_fees_usd", 0)))
            
            # For partial sells that have already happened (if any)
            already_received = (float(position.get("sell_gross_usd", 0))
                                - float(position.get("sell_fees_usd", 0)))
            
            # If we still can't find a cost basis, we assume the worst-case (0.90 per share) to avoid instant-selling
            if paid <= 1e-9:
                paid = shares * 0.90
                
            pnl = already_received + sell_gross - sell_fees - paid

            # Take profit: exit at near-break-even or better
            if pnl >= self.TAKE_PROFIT_THRESHOLD:
                return {"action": "SELL"}

            # Stop loss: cap downside
            if pnl <= -self.STOP_LOSS_PER_SHARE * shares + 1e-9:
                return {"action": "SELL"}

            # If past target, be more aggressive about exiting
            if past_target and pnl >= -0.05:
                return {"action": "SELL"}

            return {"action": "HOLD"}

        # ═══════════════════════════════════════════════════════════════
        # BUY LOGIC (flat, looking for entry)
        # ═══════════════════════════════════════════════════════════════

        # If we've already qualified and finished, just preserve cash
        if past_target:
            return {"action": "HOLD"}

        # Per-market cycle limit (adaptive with urgency)
        max_cyc = self.MAX_CYCLES_PER_MARKET
        if urgency > 1.5:
            max_cyc = min(6, max_cyc + 2)

        if self.completed_cycles >= max_cyc:
            return {"action": "HOLD"}

        # Cooldown
        if now - self.last_flat_at < self.REENTRY_COOLDOWN_S - 1e-9:
            return {"action": "HOLD"}
        if now - self.last_buy_attempt_at < self.REENTRY_COOLDOWN_S - 1e-9:
            return {"action": "HOLD"}

        # Entry window (adaptive with urgency)
        entry_window = self.ENTRY_WINDOW_S
        if urgency > 1.3:
            entry_window = min(250.0, entry_window * (1.0 + (urgency - 1.0) * 0.4))

        seconds_remaining_in_run = (self.EVAL_HOURS * 3600.0) - (now - self.run_start)
        if not (self.ENTRY_CUTOFF_S < ttc <= entry_window) or seconds_remaining_in_run <= 120.0:
            return {"action": "HOLD"}

        # ── Reference validation ──
        if not ref_valid:
            return {"action": "HOLD"}

        ref_age = now - float(ref.get("observedAt", -math.inf))
        if ref_age > self.MAX_REFERENCE_AGE_S:
            return {"action": "HOLD"}

        # Causality: target must not be from the future
        target_obs_at = float(ref.get("targetObservedAt", math.inf))
        if target_obs_at > now + 1e-9:
            return {"action": "HOLD"}

        btc = float(ref["btcMidUsd"])
        target = float(ref["openingTargetUsd"])

        # ── Signal: projected settlement gap ──
        offset = self.offset_est.offset
        raw_gap = (btc - target) - offset

        # Use TWAP-projected gap when available (more accurate)
        tw = self.twap.twap(now, lookback_s=60.0)
        if tw is not None:
            projected_gap = (tw - target) - offset
            # Weight TWAP more as we approach settlement
            w = max(0.3, min(1.0, 1.0 - (ttc - 30) / 120.0))
            effective_gap = w * projected_gap + (1.0 - w) * raw_gap
        else:
            effective_gap = raw_gap

        # Minimum gap (adaptive)
        min_gap = self.MIN_GAP_USD
        if urgency > 1.5:
            min_gap = max(5.0, min_gap * max(0.2, 2.0 - urgency))

        if abs(effective_gap) < min_gap - 1e-9:
            return {"action": "HOLD"}

        # Direction
        side = "YES" if effective_gap >= 0 else "NO"

        # ── Book quality checks ──
        side_asks = books.get(side, {}).get("asks", [])
        side_bids = books.get(side, {}).get("bids", [])
        best_asks = _levels(side_asks, reverse=False)
        best_bids = _levels(side_bids, reverse=True)

        if not best_asks:
            return {"action": "HOLD"}

        entry_price = best_asks[0][0]

        # Price band check
        if entry_price < self.MIN_ENTRY_PRICE or entry_price > self.MAX_ENTRY_PRICE:
            return {"action": "HOLD"}

        # Check ask depth is sufficient for minimum order
        ask_depth = sum(s for _, s in best_asks)
        if ask_depth < self.MIN_SHARES:
            return {"action": "HOLD"}

        # ── Determine shares to buy ──
        target_shares = min(self.TARGET_SHARES, ask_depth * 0.85)
        target_shares = max(self.MIN_SHARES, target_shares)

        # ── Cost analysis ──
        buy_result = _walk_asks(side_asks, target_shares)
        if buy_result is None:
            return {"action": "HOLD"}

        buy_gross, buy_fees, _ = buy_result
        total_cost = buy_gross + buy_fees

        # Check $5 cap
        max_spend = min(cash, self.BUY_CAP_USD - self.SAFETY_MARGIN_USD)
        if total_cost > max_spend + 1e-9:
            # Try to reduce to minimum shares
            buy_result2 = _walk_asks(side_asks, self.MIN_SHARES)
            if buy_result2 is None:
                return {"action": "HOLD"}
            buy_gross2, buy_fees2, _ = buy_result2
            total_cost2 = buy_gross2 + buy_fees2
            if total_cost2 > max_spend + 1e-9:
                return {"action": "HOLD"}
            total_cost = total_cost2
            target_shares = self.MIN_SHARES

        # ── Immediate exit check (CRITICAL — the central gate) ──
        # Never commit to a BUY without projecting full round-trip
        sell_result = _walk_bids(side_bids, target_shares)
        if sell_result is None:
            # No exit depth = no trade
            return {"action": "HOLD"}

        sell_gross, sell_fees, _ = sell_result
        immediate_pnl = sell_gross - sell_fees - total_cost

        # Adaptive loss tolerance
        max_loss = self.MAX_IMMEDIATE_LOSS_USD
        if urgency > 1.5:
            max_loss = min(0.65, max_loss * 1.3)

        # If gap is strong, allow slightly more loss (higher win probability)
        if abs(effective_gap) >= self.STRONG_GAP_USD:
            max_loss = min(0.60, max_loss * 1.2)

        if immediate_pnl < -max_loss - 1e-9:
            return {"action": "HOLD"}

        # ── COMMIT: BUY ──
        self.last_buy_attempt_at = now
        return {
            "action": "BUY",
            "outcome": side,
            "maxCashUsd": round(total_cost, 6),
        }


# ═══════════════════════════════════════════════════════════════════════
# HTTP SERVER — implements POST /decide for the evaluator
# ═══════════════════════════════════════════════════════════════════════

BOT = VelocityBot()


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != "/decide":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
            response = BOT.decide(json.loads(body))
            resp_body = json.dumps(response, separators=(",", ":")).encode()
        except Exception:
            self.send_error(400)
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp_body)))
        self.end_headers()
        self.wfile.write(resp_body)

    def log_message(self, _format: str, *_args: Any) -> None:
        return


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"Velocity Bot v2 | 127.0.0.1:{port} | POST /decide")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
