"""
FastAPI reference implementation of POST /decide — for local testing.
Requires pydantic/fastapi (not installed in this sandbox — see NOTES.md).

Run: uvicorn src.api.server:app --reload --port 8000
"""

from __future__ import annotations

import time

from fastapi import FastAPI

from src.cycle_tracker import CycleTracker
from src.decision import decide
from src.models import DecideRequest, DecideResponse

app = FastAPI(title="YeNo Volume Bot")

# NOTE: single-process in-memory state for local testing only. The real
# evaluator almost certainly manages state on its own side across calls
# — confirm this assumption against the real evaluator contract before
# relying on any persistent local state during actual evaluation.
_tracker = CycleTracker()
_run_start_time = time.time()
_run_window_seconds = 24 * 3600


@app.post("/decide", response_model=DecideResponse)
def decide_endpoint(request: DecideRequest) -> DecideResponse:
    now = time.time()
    seconds_remaining = _run_window_seconds - (now - _run_start_time)
    return decide(request, _tracker, now, seconds_remaining)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "eligible_volume": _tracker.total_eligible_volume}
