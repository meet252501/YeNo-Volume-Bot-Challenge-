# Project Plan — YeNo Volume Bot

Challenge: rolling qualification, free to enter. No fixed close date
published on the page as captured — treat that as unconfirmed, not as
"no deadline exists." Check the real challenge page for a hard date
before assuming unlimited time.

## Guiding principle

The published benchmark shows the included house bot never crosses
$1,000 across 30 development paths. Beating that isn't a formality —
it's the actual problem. Every phase below is built around the two
mechanically-grounded levers found in research: fee-curve-aware entry
selection (trade near the extremes, not near 50¢) and disciplined,
complete-cycle-only volume accounting.

---

## Phase 0 — Setup & baseline reproduction (Day 0-2)
- [ ] Download the real starter kit, House Bot v1 source, tested
      configurations, and evaluator contract from the challenge page
- [ ] Set up Python env, pin dependencies
- [ ] Get House Bot v1 running against local replay data
- [ ] Confirm reproduced numbers are in the same neighborhood as the
      published benchmark ($559 median, $943 best, 18/30 flat, $680
      median-among-flat)
- [ ] If numbers diverge significantly, treat this as a backtest-harness
      bug to fix before anything else

## Phase 1 — Contract verification (Day 1-2, overlaps Phase 0)
- [ ] Reconcile `docs/data_schema.md` against the real evaluator contract
- [ ] Resolve every open question listed there (position shape, HOLD
      body requirements, malformed-response handling, unfillable-BUY
      behavior)

## Phase 2 — Core decision engine (Day 2-6)
- [ ] `src/fees.py` — both fee layers, golden test against the brief's
      own $5.00/$4.91/$9.91 example
- [ ] `src/cycle_tracker.py` — complete-cycle-only accounting, partial
      fill handling
- [ ] `src/risk.py` — sizing with safety margin, favorite-longshot
      haircut, drawdown circuit-breaker, flatten-by-deadline logic
- [ ] `src/decision.py` — wires the above into HOLD/BUY/SELL, with state
      validation (staleness, entry cutoff) as the first gate every time

## Phase 3 — Backtest harness (Day 3-6, overlaps Phase 2)
- [ ] `src/backtest/replay.py` — runs decision engine against replay paths
- [ ] `src/backtest/report.py` — matches Builderr's published report
      shape (median, best, worst, flat %, stressed numbers)
- [ ] Stress-test mode (2-cent adverse execution) implemented and
      reported alongside every baseline run

## Phase 4 — Strategy iteration (Day 6-14)
- [ ] Learning harness loop running (`docs/learning_harness.md`)
- [ ] Milestone: beat the house bot's $943 best on at least one path
- [ ] Milestone: beat the house bot's $559 median across all paths
- [ ] Milestone: first replay path crossing $1,000 while finishing flat
- [ ] Milestone: majority of replay paths crossing $1,000 while flat
- [ ] Every promoted change logged with baseline AND stressed numbers

## Phase 5 — Hardening (Day 12-16, overlaps Phase 4)
- [ ] Ambiguous-timeout reconciliation logic tested explicitly
- [ ] Entry-cutoff and staleness rejection tested explicitly, not just
      implicitly covered by the replay run
- [ ] Confirm zero outbound network dependency (run in a
      no-network container and confirm it still behaves correctly on
      replay data)

## Phase 6 — Freeze & submit (once Phase 4 milestones are solid)
- [ ] Full pre-submission checklist in `docs/SUBMISSION.md`
- [ ] Freeze commit/container, confirm reproducibility from a clean
      checkout
- [ ] Submit per whichever mode (repo vs. HTTPS endpoint) is confirmed
      correct in Phase 1

---

## Milestone checkpoints

| Milestone | Target |
|---|---|
| House bot baseline reproduced | Day 2 |
| Core decision engine passes golden tests | Day 6 |
| First strategy beats house bot's median | Day 8-10 |
| First replay path crosses $1,000 flat | Day 10-14 |
| Majority of paths cross $1,000 flat, stressed numbers still flat 100% | Day 14-16 |
| Frozen, submitted | As soon as milestones above are solid — this is rolling qualification, no need to wait for a fixed date once genuinely ready |

## Risks to watch
- **Overfitting to the 30 development paths** — the real evaluation uses
  an unseen window; prefer mechanically-justified strategy changes.
- **Fee-estimate mismatch with the evaluator's real math** — always
  leave a safety margin on the $5.00 cap, never request exactly $5.00.
- **Chasing $1,000 at the cost of flat-finish reliability** — a bot that
  hits $1,000 but doesn't finish flat scores nothing; 100% flat rate is
  worth more than a higher median with any non-flat paths.
