"""Shared pytest fixtures."""

import json
from pathlib import Path

import pytest

GOLDEN_DIR = Path(__file__).parent / "golden"


@pytest.fixture
def sample_request_json():
    return json.loads((GOLDEN_DIR / "sample_request.json").read_text())


@pytest.fixture
def worked_example():
    return json.loads((GOLDEN_DIR / "worked_example_cycle.json").read_text())
