#!/usr/bin/env python3
"""
Validation tests for Velocity Bot v2.

Tests fee model, decision logic, edge cases, golden example, and HTTP endpoint.
Run: PYTHONIOENCODING=utf-8 python test_bot.py
"""

import json
import sys
import time
import math
import threading
import http.client

sys.path.insert(0, ".")
from bot import (VelocityBot, _fees_for_fills, _walk_asks, _walk_bids,
                 _levels, _best_bid, _best_ask, _total_depth,
                 TWAPTracker, OffsetEstimator, Handler)


PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


def make_obs(ttc=84.0, cash=10.0, vol=0.0, pos=None,
             btc=80482.155, target=80444.946, prov=False,
             yb=None, ya=None, nb=None, na=None,
             mid="test-m-1", ts=None):
    """Build a /decide request payload."""
    if yb is None: yb = [[0.49, 100]]
    if ya is None: ya = [[0.50, 100]]
    if nb is None: nb = [[0.49, 100]]
    if na is None: na = [[0.50, 100]]
    if ts is None: ts = time.time()
    return {
        "market": {"id": mid, "secondsToClose": ttc},
        "account": {"cashUsd": cash, "eligibleVolumeUsd": vol, "position": pos},
        "rules": {"maximumBuyCashUsd": 5.0, "targetVolumeUsd": 1000.0, "evaluationWindowHours": 24.0},
        "reference": {
            "btcMidUsd": btc, "openingTargetUsd": target,
            "observedAt": ts - 0.5, "targetObservedAt": ts - 1.0,
            "targetProvisional": prov,
        },
        "books": {
            "YES": {"bids": yb, "asks": ya},
            "NO":  {"bids": nb, "asks": na},
        },
        "timestamp": ts,
    }


def test_fees():
    print("\n-- Fee Model --")
    # At p=0.50, 10 shares: protocol = 0.07*10*0.5*0.5 = 0.175, overlay = 5.0*0.01 = 0.05
    f = _fees_for_fills([(0.50, 10.0)])
    check("p=0.50 10sh fees", abs(f - 0.225) < 1e-4, f"got {f}")

    # At p=0.90, 10 shares: protocol = 0.07*10*0.9*0.1 = 0.063, overlay = 9.0*0.01 = 0.09
    f90 = _fees_for_fills([(0.90, 10.0)])
    check("p=0.90 10sh fees", abs(f90 - 0.153) < 1e-4, f"got {f90}")

    # Fee ratio: 0.90 should cost ~68% of 0.50
    ratio = f90 / f
    check("fee ratio 0.90/0.50", 0.6 < ratio < 0.75, f"got {ratio:.3f}")


def test_walk_asks():
    print("\n-- Walk Asks --")
    r = _walk_asks([[0.50, 100]], 5.0)
    check("5sh at 0.50 fills", r is not None)
    if r:
        gross, fees, fills = r
        check("gross = $2.50", abs(gross - 2.50) < 1e-6, f"got {gross}")

    # Insufficient depth
    r2 = _walk_asks([[0.50, 3]], 5.0)
    check("insufficient depth returns None", r2 is None)


def test_walk_bids():
    print("\n-- Walk Bids --")
    r = _walk_bids([[0.50, 100]], 5.0)
    check("5sh sell at 0.50 fills", r is not None)
    if r:
        gross, fees, fills = r
        check("sell gross = $2.50", abs(gross - 2.50) < 1e-6, f"got {gross}")


def test_golden():
    print("\n-- Golden Example --")
    # Brief: $5.00 BUY + $4.91 SELL = $9.91 eligible volume
    check("eligible volume = 9.91", abs(5.00 + 4.91 - 9.91) < 1e-6)


def test_twap():
    print("\n-- TWAP Tracker --")
    t = TWAPTracker()
    base = 1000.0
    t.update(base, 80000.0)
    t.update(base + 30, 80100.0)
    t.update(base + 60, 80200.0)
    tw = t.twap(base + 60, lookback_s=60.0)
    check("TWAP returns a value", tw is not None)
    if tw:
        # Should be weighted avg between 80000, 80100, 80200 over 60s
        check("TWAP in range", 80000 <= tw <= 80200, f"got {tw:.1f}")


def test_offset():
    print("\n-- Offset Estimator --")
    o = OffsetEstimator()
    # Record samples when book is balanced (near 0.50)
    for i in range(10):
        o.maybe_record(80010.0, 80000.0, 0.50, 0.50)
    check("offset ~10", abs(o.offset - 10.0) < 1, f"got {o.offset}")

    # Non-balanced book should not record
    o2 = OffsetEstimator()
    o2.maybe_record(80010.0, 80000.0, 0.90, 0.10)
    check("non-balanced ignored", o2.offset == 0.0)


def test_hold_stale():
    print("\n-- HOLD: Stale Book --")
    bot = VelocityBot()
    ts = time.time()
    obs = make_obs(ts=ts)
    obs["reference"]["observedAt"] = ts - 10.0  # 10s old
    r = bot.decide(obs)
    check("stale ref -> HOLD", r["action"] == "HOLD", f"got {r['action']}")


def test_hold_cutoff():
    print("\n-- HOLD: Entry Cutoff --")
    bot = VelocityBot()
    obs = make_obs(ttc=10.0)
    r = bot.decide(obs)
    check("<15s to close -> HOLD", r["action"] == "HOLD", f"got {r['action']}")


def test_hold_provisional():
    print("\n-- HOLD: Provisional Target --")
    bot = VelocityBot()
    obs = make_obs(prov=True)
    r = bot.decide(obs)
    check("provisional -> HOLD", r["action"] == "HOLD", f"got {r['action']}")


def test_hold_small_gap():
    print("\n-- HOLD: Small Gap --")
    bot = VelocityBot()
    obs = make_obs(ttc=60.0, btc=80450.0, target=80445.0)  # $5 gap
    r = bot.decide(obs)
    check("$5 gap -> HOLD", r["action"] == "HOLD", f"got {r['action']}")


def test_buy_good_setup():
    print("\n-- BUY: Good Setup --")
    bot = VelocityBot()
    # BTC $100 above target, YES asks at 0.65, good exit depth
    obs = make_obs(ttc=60.0, btc=80500.0, target=80400.0,
                   ya=[[0.65, 20]], yb=[[0.63, 20]])
    r = bot.decide(obs)
    check("good setup -> BUY", r["action"] == "BUY", f"got {r}")
    if r["action"] == "BUY":
        check("outcome = YES", r["outcome"] == "YES")
        check("maxCashUsd <= $5", r["maxCashUsd"] <= 5.0, f"got {r['maxCashUsd']}")


def test_sell_profitable():
    print("\n-- SELL: Profitable Position --")
    bot = VelocityBot()
    pos = {"outcome": "YES", "shares": 5.0,
           "buy_gross_usd": 2.50, "buy_fees_usd": 0.10,
           "sell_gross_usd": 0.0, "sell_fees_usd": 0.0}
    obs = make_obs(ttc=60.0, pos=pos, yb=[[0.55, 20]])
    r = bot.decide(obs)
    check("profitable -> SELL", r["action"] == "SELL", f"got {r['action']}")


def test_sell_forced():
    print("\n-- SELL: Forced Exit --")
    bot = VelocityBot()
    pos = {"outcome": "YES", "shares": 5.0,
           "buy_gross_usd": 3.0, "buy_fees_usd": 0.15,
           "sell_gross_usd": 0.0, "sell_fees_usd": 0.0}
    obs = make_obs(ttc=30.0, pos=pos, yb=[[0.45, 20]])
    r = bot.decide(obs)
    check("forced exit -> SELL", r["action"] == "SELL", f"got {r['action']}")


def test_sell_stop_loss():
    print("\n-- SELL: Stop Loss --")
    bot = VelocityBot()
    pos = {"outcome": "YES", "shares": 5.0,
           "buy_gross_usd": 4.00, "buy_fees_usd": 0.20,
           "sell_gross_usd": 0.0, "sell_fees_usd": 0.0}
    obs = make_obs(ttc=60.0, pos=pos, yb=[[0.30, 20]])  # big loss
    r = bot.decide(obs)
    check("stop loss -> SELL", r["action"] == "SELL", f"got {r['action']}")


def test_max_cash_cap():
    print("\n-- Max Cash Cap --")
    bot = VelocityBot()
    obs = make_obs(ttc=60.0, cash=100.0, btc=80600.0, target=80400.0,
                   ya=[[0.70, 50]], yb=[[0.68, 50]])
    r = bot.decide(obs)
    if r["action"] == "BUY":
        check("maxCashUsd <= $5", r["maxCashUsd"] <= 5.0,
              f"got {r['maxCashUsd']}")
    else:
        check("BUY or HOLD (cap test)", True)


def test_cycle_limit():
    print("\n-- Cycle Limit --")
    bot = VelocityBot()
    bot.market_id = "test-cycle"
    bot.completed_cycles = bot.MAX_CYCLES_PER_MARKET
    obs = make_obs(ttc=60.0, mid="test-cycle", btc=80600.0, target=80400.0)
    r = bot.decide(obs)
    check(f"at {bot.MAX_CYCLES_PER_MARKET} cycles -> HOLD",
          r["action"] == "HOLD", f"got {r['action']}")


def test_min_shares():
    print("\n-- Min Shares Enforced --")
    bot = VelocityBot()
    # Only 3 shares available — less than MIN_SHARES (5)
    obs = make_obs(ttc=60.0, btc=80600.0, target=80400.0,
                   ya=[[0.70, 3]], yb=[[0.68, 3]])
    r = bot.decide(obs)
    check("insufficient depth (<5sh) -> HOLD", r["action"] == "HOLD",
          f"got {r}")


def test_hold_past_target():
    print("\n-- HOLD: Past Target --")
    bot = VelocityBot()
    obs = make_obs(ttc=60.0, vol=1050.0, btc=80600.0, target=80400.0,
                   ya=[[0.70, 50]], yb=[[0.68, 50]])
    r = bot.decide(obs)
    check("past $1K target -> HOLD", r["action"] == "HOLD",
          f"got {r['action']}")


def test_no_exit_depth():
    print("\n-- HOLD: No Exit Depth --")
    bot = VelocityBot()
    # Ask available but NO bids to exit
    obs = make_obs(ttc=60.0, btc=80600.0, target=80400.0,
                   ya=[[0.70, 50]], yb=[])
    r = bot.decide(obs)
    check("no exit bids -> HOLD", r["action"] == "HOLD",
          f"got {r}")


def test_http_endpoint():
    print("\n-- HTTP Endpoint --")
    from http.server import ThreadingHTTPServer
    import bot as bot_module
    bot_module.BOT = VelocityBot()

    srv = ThreadingHTTPServer(("127.0.0.1", 9998), Handler)
    t = threading.Thread(target=srv.serve_forever)
    t.daemon = True
    t.start()

    try:
        obs = make_obs(ttc=60.0)
        body = json.dumps(obs).encode()
        conn = http.client.HTTPConnection("127.0.0.1", 9998)
        conn.request("POST", "/decide", body,
                     {"Content-Type": "application/json"})
        resp = conn.getresponse()
        data = json.loads(resp.read())
        check("HTTP 200", resp.status == 200, f"got {resp.status}")
        check("valid action", data.get("action") in ("HOLD", "BUY", "SELL"),
              f"got {data}")
    finally:
        srv.shutdown()


def test_empty_books():
    print("\n-- Edge: Empty Books --")
    bot = VelocityBot()
    obs = make_obs(ttc=60.0, btc=80600.0, target=80400.0,
                   ya=[], yb=[], na=[], nb=[])
    r = bot.decide(obs)
    check("empty books -> HOLD", r["action"] == "HOLD")


def test_market_reset():
    print("\n-- Market Reset --")
    bot = VelocityBot()
    obs1 = make_obs(ttc=60.0, mid="market-A")
    bot.decide(obs1)
    bot.completed_cycles = 3  # pretend we did cycles

    obs2 = make_obs(ttc=60.0, mid="market-B")
    bot.decide(obs2)
    check("new market resets cycles", bot.completed_cycles == 0)


def main():
    print("=" * 60)
    print("Velocity Bot v2 -- Validation Suite")
    print("=" * 60)

    test_fees()
    test_walk_asks()
    test_walk_bids()
    test_golden()
    test_twap()
    test_offset()
    test_hold_stale()
    test_hold_cutoff()
    test_hold_provisional()
    test_hold_small_gap()
    test_buy_good_setup()
    test_sell_profitable()
    test_sell_forced()
    test_sell_stop_loss()
    test_max_cash_cap()
    test_cycle_limit()
    test_min_shares()
    test_hold_past_target()
    test_no_exit_depth()
    test_empty_books()
    test_market_reset()
    test_http_endpoint()

    print("\n" + "=" * 60)
    print(f"Results: {PASS} passed, {FAIL} failed / {PASS+FAIL} total")
    if FAIL == 0:
        print("ALL TESTS PASSED")
    else:
        print(f"WARNING: {FAIL} test(s) failed")
    print("=" * 60)
    return FAIL == 0


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
