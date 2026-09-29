"""
Tests for src/decision.py. Requires pydantic (via src/models.py) —
NOT executed in the sandbox that built this scaffold (no pydantic,
no network to install it). Run `make dev-install && pytest tests/test_decision.py -v`
in a real environment to confirm before trusting this file.
"""

from src.decision import entry_score, validate_state
from src.models import DecideRequest


def test_validate_state_flags_stale_book(sample_request_json):
    req = DecideRequest.model_validate(sample_request_json)
    now = req.reference.observedAt + 5.0  # 5s later -> stale (>2s threshold)
    assert validate_state(req, now) == "stale_book"


def test_validate_state_flags_entry_cutoff(sample_request_json):
    sample_request_json["market"]["secondsToClose"] = 10  # < 15s cutoff
    req = DecideRequest.model_validate(sample_request_json)
    now = req.reference.observedAt
    assert validate_state(req, now) == "entry_cutoff"


def test_validate_state_clear_when_fresh_and_time_remains(sample_request_json):
    req = DecideRequest.model_validate(sample_request_json)
    now = req.reference.observedAt + 0.5
    assert validate_state(req, now) is None


def test_entry_score_prefers_band_edges_over_midpoint_within_band():
    """Updated per docs/RESEARCH.md §7b correction: 0.90 is now OUTSIDE
    the tested-profitable band (0.30-0.80) and scores 0, not higher than
    midpoint. Compare within-band values instead."""
    score_mid = entry_score(0.50, causal_signal_aligned=True)
    score_band_edge = entry_score(0.30, causal_signal_aligned=True)
    assert score_band_edge > score_mid


def test_entry_score_zero_outside_tested_band():
    """0.90 is outside the 0.30-0.80 band per the corrected research —
    must score 0 regardless of how far it is from the midpoint."""
    assert entry_score(0.90, causal_signal_aligned=True) == 0.0
    assert entry_score(0.10, causal_signal_aligned=True) == 0.0
