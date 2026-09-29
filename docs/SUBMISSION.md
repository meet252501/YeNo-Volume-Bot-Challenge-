# Submission Package Template

## Submission info
- **Commit hash / container digest (frozen):**
- **Date/time frozen:**
- **Submission mode:** repository URL OR HTTPS endpoint (confirm which
  Builderr actually wants before freezing — the brief mentions both
  "Submit a repository or HTTPS endpoint")

## Pre-freeze checklist (must all pass)
- [ ] Full 30-path replay run completed and logged
- [ ] 100% of replay paths finish flat
- [ ] No BUY across any path exceeded $5.00 including fees
- [ ] Stressed run (2-cent adverse execution) still finishes flat on
      every single path
- [ ] House bot baseline reproduced locally before trusting comparisons
- [ ] Worked fee example ($5.00 buy / $4.91 sell / $9.91 credited)
      passes as a golden test
- [ ] Staleness (>2s book), entry-cutoff (<15s), and flatten-by-deadline
      logic each have a dedicated passing test, not just implicit
      coverage via the replay run
- [ ] No outbound network calls anywhere in the decision path — confirm
      by running the bot in a container with no network access, per the
      evaluator's own stated constraint
- [ ] Dependencies pinned to exact versions, reproducible from a clean
      checkout

## Results summary (fill in before submitting)
- Median ending cash across replay set:
- Best / worst:
- % paths flat:
- % paths hit $1,000:
- Stressed median / worst:

## Known limitations (be honest here, same discipline as everywhere else)
- [State clearly if the bot has not yet crossed $1,000 in backtest —
  per the published benchmark, no bot had as of the challenge page
  snapshot, so this may be expected, not a disqualifying admission]
