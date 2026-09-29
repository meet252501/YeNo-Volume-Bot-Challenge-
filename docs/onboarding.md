# Onboarding — First Hour on This Project

1. Read `README.md`, then `AGENTS.md` in full.
2. Read `docs/challenge_brief_summary.md` — this is what you're actually
   being scored against.
3. Read `docs/RESEARCH.md` — this is *why* the algorithm docs say what
   they say; don't skip it and jump straight to the algorithms.
4. Skim all seven files in `docs/algorithms/` — even a fast read gives
   the full mental model before touching code.
5. Run `make dev-install` in a real environment (this scaffold was built
   in a sandbox with no network/pip access — see `NOTES.md` for exactly
   what was and wasn't verified as a result).
6. Run `pytest tests/test_fees.py tests/test_cycle_tracker.py tests/test_risk.py -v`
   — these were verified passing (17/17 assertions) with pure Python
   during scaffold creation; confirm they still pass in your environment.
7. Run `pytest tests/test_decision.py -v` — this needs pydantic and was
   **not** verified during scaffold creation; this is your first real
   checkpoint in a working environment.
8. Move to `TODO.md` Phase 0 — download the real starter kit and
   reproduce the house bot's published benchmark before writing any new
   strategy code.
