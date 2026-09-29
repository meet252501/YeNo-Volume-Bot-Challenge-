# Environment Setup

## Requirements
- Python 3.11+
- No API keys or credentials needed — this challenge is code-only,
  never touches a real account (see `SECURITY.md`)

## Setup
```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
make dev-install
cp .env.example .env        # no real secrets needed, just path config
```

## Verify the environment works
```bash
make check    # lint + all tests
```

Expect `test_fees.py`, `test_cycle_tracker.py`, and `test_risk.py` to
pass cleanly — these were verified with pure Python during scaffold
creation (see `NOTES.md`). `test_decision.py` needs pydantic/fastapi
installed and was not verified in the original scaffold sandbox — this
is your first real checkpoint.

## Docker (optional, useful for the no-network sanity check)
```bash
docker build -t yeno-bot .
docker run --network=none yeno-bot python -c "from src.decision import decide"
```
This confirms the bot's core import path doesn't secretly depend on
network access — matching the evaluator's own stated constraint that
official runs block arbitrary outbound network.

## Getting the real replay/starter-kit data
Not included in this repo (respect any licensing/size constraints on
Builderr's data) — see `scripts/download_starter_kit.py` (currently a
placeholder — fill in the real URLs from the challenge page) and
`TODO.md` Phase 0.
