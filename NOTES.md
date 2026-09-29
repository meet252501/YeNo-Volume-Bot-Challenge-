# Working Notes / Daily Log

## Template
```
### YYYY-MM-DD
- Did:
- Learned:
- Blocked on:
- Next:
```

### 2026-09-22
- Did: initial scaffold — docs, plan, algorithm specs, bot skeleton
- Learned: house bot's own published benchmark never crosses $1,000
  (best $943, median $559 across 30 paths) — this is a genuinely open
  problem, not a solved template. Under 2-cent adverse-execution stress
  the best run fell to $385, median to $70 — the strategy needs to be
  robust to worse execution than the happy-path numbers suggest.
- Blocked on: nothing yet — next session starts by reproducing the
  house bot's benchmark locally
- Next: download real starter kit, verify data_schema.md against it

### 2026-09-25 (research deep-dive)
- Did: extensive web research pass — found a real, rigorously-tested
  competitor repo (AnSa30-06/yeno-late-favourite) for this exact
  challenge, plus adjacent strategy research and some explicitly
  unreliable sources (flagged and excluded, not cited)
- Learned: two significant corrections to the original design —
  (1) settlement is TWAP-based (last 60s mean vs pre-open 60s mean,
  98% match to real winners), not last-price; (2) the price-band
  guidance was wrong to treat "more extreme = always better" — real
  tested data shows a bounded 0.30-0.80 sweet spot, with entries above
  ~0.90 losing money on the week. Fixed both docs AND the actual code
  (src/risk.py, src/decision.py), then re-verified with pure Python
  that the fix genuinely changes the scoring outcome (0.90 now
  correctly scores 0 instead of being preferred over 0.50).
- Blocked on: still don't have the real evaluator contract to confirm
  the settlement/dual-feed findings apply identically to YeNo (vs. the
  Polymarket data they were derived from) — flagged as open items in
  the relevant docs, not assumed confirmed.
- Next: read yeno-late-favourite's actual bot.py/tests in full (not
  just README-level summary) before finalizing src/decision.py's exit
  logic around the settlement-mechanics finding.
