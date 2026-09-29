# AGENTS.md — Build Instructions for Autonomous Coding Agents

Read this fully before writing code. This project has a genuinely
unsolved target (per the published house-bot benchmark, no bot has
crossed $1,000 as of the challenge page snapshot) — treat that as real
signal about difficulty, not flavor text to skip past.

## Reality check, stated plainly

This is a real trading/execution problem with a hard, adversarial fee
structure and realistic execution modeling (latency, partial fills,
staleness rules). No amount of clever prompt-following replaces
actually running the backtest harness and reading the numbers. Every
claim in these docs about fee mechanics has been verified against real,
current Polymarket documentation (see `docs/RESEARCH.md`) — trust that
grounding, but verify the exact `/decide` contract against Builderr's
real downloadable evaluator contract before treating anything in
`docs/data_schema.md` as final, since it was reconstructed from a
challenge-page example, not a fetched spec file.

## Build order (do not reorder)

1. **Phase 0 — reproduce the baseline.** Get House Bot v1 running
   against local replay data and confirm you can reproduce something
   close to the published benchmark ($559 median, $943 best, 18/30
   flat) before changing anything. If you can't reproduce it, the
   backtest harness has a bug — fix that first, not the strategy.
2. **Phase 1 — verify the contract.** Download the real evaluator
   contract and reconcile every open question in `docs/data_schema.md`
   against it. Update the doc with what you find.
3. **Phase 2 — implement the fee-aware decision core**
   (`src/fees.py`, `src/decision.py`, `src/risk.py`,
   `src/cycle_tracker.py`) per the algorithm docs in `docs/algorithms/`.
4. **Phase 3 — iterate via the learning harness**
   (`docs/learning_harness.md`) — every change gets a full replay run,
   baseline AND stressed numbers, before being considered an improvement.
5. **Phase 4 — freeze and submit** per `docs/SUBMISSION.md`'s checklist.

## Non-negotiable design rules

1. **Every decision projects full round-trip fees first** — never commit
   to a BUY without running the entry+exit fee estimate through
   `src/fees.py`.
2. **Flatten-by-deadline overrides every other consideration.** A
   marginally worse exit is always better than finishing non-flat.
3. **Never retry blindly after a timeout** — always reconcile actual
   evaluator-reported state first.
4. **Report stressed (2-cent adverse execution) numbers alongside every
   baseline result** — a strategy that only looks good under perfect
   execution is not validated.
5. **Apply the favorite-longshot haircut** — don't trust a 0.90+ or
   0.10- price as literally that confident; see `docs/RESEARCH.md` §4.
6. **No component assumes live network access during evaluation** — the
   evaluator blocks outbound network; everything must come through the
   `/decide` request payload itself.

## Definition of done, per phase
Not "code exists" — the actual bar:
- [ ] House bot baseline reproduced within a reasonable tolerance of the
      published numbers
- [ ] Strategy change shows improved median AND maintains 100% flat rate
      across the full replay set
- [ ] Stressed numbers reported and reviewed, not just baseline
- [ ] Golden test (the brief's own $5.00/$4.91/$9.91 example) passes
- [ ] `make check` passes clean

## What NOT to do
- Do not report only best-case backtest numbers — median and worst
  matter more for a realistic assessment.
- Do not assume the evaluator's fee math matches a local estimate to
  the cent — always leave a safety margin on the $5.00 BUY cap.
- Do not build any strategy component that assumes a live external data
  source during evaluation.
- Do not treat "no bot has crossed $1,000 yet" as evidence the target
  is impossible — treat it as evidence that a genuinely well-reasoned
  approach, not a copy of the house bot with minor tweaks, is needed.
