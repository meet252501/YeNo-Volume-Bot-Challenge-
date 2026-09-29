# Contributing / Working Notes

## Workflow
1. Branch off `main`: `feature/<short-name>`
2. Run `make check` (lint + tests) before committing
3. Never commit a strategy change without a backtest run attached in
   the PR description (median/best/worst across the replay set, flat
   rate, drawdown under stress)
4. Tag a commit as frozen right before submission — see
   `docs/SUBMISSION.md`

## Code style
- Python, `ruff` for lint + format
- Type hints on all public functions
- No global mutable state in the decision function — it must be safe
  to call repeatedly with fresh state each time, matching how the
  real evaluator will call it

## Never commit
- `.env`, API keys, or credentials (none needed for this challenge,
  but keep the habit)
- Anything under `data/replay/` if it's a large licensed dataset —
  check size/licensing before committing bulk replay data
