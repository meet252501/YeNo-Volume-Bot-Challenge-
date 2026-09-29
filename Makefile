.PHONY: install dev-install lint format test check backtest serve

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements-dev.txt

lint:
	ruff check .

format:
	ruff format .

test:
	pytest -v

check: lint test

backtest:
	python scripts/run_backtest.py --replay-dir data/replay --report out/backtest-report.json

serve:
	uvicorn src.api.server:app --reload --port 8000
