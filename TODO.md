# TODO

## First step, before anything else
- [ ] Read `AGENTS.md` in full
- [ ] Download the real starter kit (.zip), House Bot v1 source, tested
      configurations, and evaluator contract from the Builderr challenge
      page — this project's docs are built from the challenge page text
      only; the real downloadable evaluator contract may have more
      precise detail than what's summarized here
- [ ] Confirm the exact `/decide` request/response schema against the
      real evaluator contract, not just `docs/data_schema.md`'s working
      copy

## Phase 0 — setup
- [ ] Python env, pin dependency versions in `requirements.txt`
- [ ] Get House Bot v1 running locally against replay data, reproduce
      its published benchmark numbers ($559 median, $943 best) before
      changing anything — if you can't reproduce their baseline, your
      backtest harness has a bug, not their bot
- [ ] Set up the learning harness (see `docs/learning_harness.md`)

## Ongoing
- [ ] Every strategy change gets a full 30-path replay run before
      being considered "done"
- [ ] Track every run's median/best/worst, flat-rate (%), and stressed
      (2-cent adverse execution) result in a trial log
- [ ] Keep `PROJECT_PLAN.md` phase checkboxes current

## Before submission
- [ ] Confirm the bot finishes flat in 100% of replay paths, not just
      most — a single non-flat ending disqualifies the real run
- [ ] Confirm max-per-BUY never exceeds $5 including fees, on every
      single decision, not just typical ones
- [ ] Confirm the bot handles a "books older than 2 seconds" rejection
      and the "no new entries in final 15 seconds" rule without crashing
      or hanging
- [ ] Freeze a commit/container digest, verify it's reproducible from
      a clean checkout
