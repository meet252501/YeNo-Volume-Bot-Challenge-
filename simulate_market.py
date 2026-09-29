import json
import time
import math
from bot import VelocityBot

def run_deep_simulation():
    print("=" * 60)
    print("DEEP TEST SIMULATION: 5-Minute Market Lifecycle")
    print("=" * 60)
    
    bot = VelocityBot()
    run_start = time.time()
    
    # Simulate a market closing in 300 seconds
    market_id = "shohum-sim-1"
    cash = 10.0
    vol = 0.0
    position = None
    
    # Market parameters
    btc = 80000.0
    target = 80000.0
    
    actions_taken = []
    
    for sec in range(0, 301, 5): # tick every 5 seconds
        ttc = 300.0 - sec
        now = run_start + sec
        
        # Simulate price drift
        if sec > 60:
            btc += 2.0 # BTC drifts up by $2 every 5s, creating a gap
            
        gap = btc - target
        
        # YES is more likely. Let's simulate a lagging book.
        yes_price = 0.40
        no_price = 0.60
        
        # Feed the TWAP and offset
        bot.twap.update(now, btc)
        bot.offset_est.maybe_record(btc, target, yes_price, no_price)
        
        obs = {
            "market": {"id": market_id, "secondsToClose": ttc},
            "account": {"cashUsd": cash, "eligibleVolumeUsd": vol, "position": position},
            "rules": {"maximumBuyCashUsd": 5.0, "targetVolumeUsd": 1000.0, "evaluationWindowHours": 24.0},
            "reference": {
                "btcMidUsd": btc, "openingTargetUsd": target,
                "observedAt": now - 0.5, "targetObservedAt": now - 1.0,
                "targetProvisional": False,
            },
            "books": {
                "YES": {"bids": [[yes_price - 0.01, 100]], "asks": [[yes_price, 100]]},
                "NO":  {"bids": [[no_price - 0.01, 100]], "asks": [[no_price, 100]]},
            },
            "timestamp": now,
        }
        
        response = bot.decide(obs)
        action = response.get("action")
        
        if action == "BUY":
            outcome = response["outcome"]
            max_cash = response["maxCashUsd"]
            shares = 10.0
            price = yes_price if outcome == "YES" else no_price
            paid = (shares * price) + (0.07 * shares * price * (1-price)) + (max_cash * 0.01)
            cash -= paid
            position = {
                "outcome": outcome,
                "shares": shares,
                "notional_paid": paid
            }
            actions_taken.append(f"T-{ttc}s: BUY {outcome} (10sh) -> Cash: ${cash:.2f}")
            
        elif action == "SELL":
            if position:
                shares = position["shares"]
                outcome = position["outcome"]
                
                # Market realizes the gap and price spikes near the end
                if gap > 30 and ttc < 60:
                    price = 0.90 
                else:
                    price = (yes_price - 0.01) if outcome == "YES" else (no_price - 0.01)
                    
                gross = shares * price
                fees = (0.07 * shares * price * (1-price)) + (gross * 0.01)
                net = gross - fees
                cash += net
                vol += (position["notional_paid"] + gross)
                actions_taken.append(f"T-{ttc}s: SELL {outcome} (10sh) @ {price:.2f} -> Cash: ${cash:.2f}, Vol: ${vol:.2f}")
                position = None
                
    print("\n--- Simulation Results ---")
    if not actions_taken:
        print("Bot properly held (waited for the right entry conditions).")
    for a in actions_taken:
        print(a)
    print(f"\nFinal Cash: ${cash:.2f} (Start: $10.00)")
    print(f"Total Eligible Volume: ${vol:.2f}")
    if position:
        print("WARNING: Finished with open position!")
    else:
        print("Successfully finished flat.")
    print("============================================================")

if __name__ == "__main__":
    run_deep_simulation()
