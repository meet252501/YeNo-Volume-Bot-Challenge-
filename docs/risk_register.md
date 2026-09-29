# Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Bot fails to finish flat on the real (unseen) evaluation window | Medium | High (total disqualification, not partial credit) | Flatten-by-deadline logic tested independently of strategy logic; hard safety-buffer seconds, not a probabilistic decision |
| Strategy overfit to the 30 development replay paths | Medium | High | Prefer mechanically-justified changes (fee curve, execution realism) over changes that just happen to score well locally |
| BUY exceeds $5.00 due to fee-estimate mismatch with evaluator's real fee math | Low-Medium | High (hard qualification failure) | Safety margin below the cap, not an exact-to-the-cent request |
| Ambiguous-timeout retry accidentally opens a duplicate position | Low | High | Mandatory state-reconciliation step before any retry, never blind retry |
| Backtest harness itself has a bug, invalidating all strategy comparisons | Medium | High | Reproduce the published house-bot benchmark first, before trusting any derived comparison |
| Strategy looks good under baseline execution but collapses under adverse-execution stress | Medium | Medium-High | Every trial reports stressed numbers alongside baseline, non-optional |
| Running out of usable capital mid-window with no path to recover | Medium | High | Drawdown circuit-breaker; pacing math against elapsed time, not per-market forcing |
| No bot has crossed $1,000 as of the published benchmark — the target may be very difficult with current market conditions | High | Medium (affects expectations, not correctness) | Set realistic internal milestones (e.g. "beat the house bot's $943 best" before "cross $1,000"); treat any qualifying result as a genuine achievement, not a given |
