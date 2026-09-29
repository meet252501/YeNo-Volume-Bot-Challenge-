"""
Replay harness skeleton — runs the decision engine against local replay
paths. NOT yet wired to real replay data (data/replay/ is empty until
the real starter kit's replay set is downloaded — see TODO.md Phase 0).
"""
from __future__ import annotations

import json
from pathlib import Path

from src.backtest.report import ReplayReport


def load_replay_paths(replay_dir: Path) -> list[dict]:
    paths = []
    for f in sorted(replay_dir.glob("*.json")):
        paths.append(json.loads(f.read_text()))
    return paths


def run_replay_path(path_data: dict, stressed: bool = False) -> tuple[float, bool, bool]:
    """
    Returns (ending_cash, finished_flat, hit_target).
    STUB — wire this to actually replay the decision engine tick-by-tick
    against path_data once real replay data is available. Currently
    raises to avoid silently reporting fake numbers.
    """
    raise NotImplementedError(
        "Wire this to the real decision engine + replay data format once "
        "the real starter kit's replay set is downloaded (see TODO.md Phase 0). "
        "Do not fake this function's output — an unimplemented backtest "
        "must fail loudly, not report invented numbers."
    )


def run_full_replay(replay_dir: Path) -> ReplayReport:
    paths = load_replay_paths(replay_dir)
    if not paths:
        raise FileNotFoundError(
            f"No replay data found in {replay_dir} — download the real "
            f"starter kit's replay set first (see TODO.md Phase 0)."
        )

    baseline_results, stressed_results = [], []
    flat_count, hit_target_count = 0, 0

    for path_data in paths:
        cash, flat, hit_target = run_replay_path(path_data, stressed=False)
        baseline_results.append(cash)
        flat_count += int(flat)
        hit_target_count += int(hit_target)

        stressed_cash, _, _ = run_replay_path(path_data, stressed=True)
        stressed_results.append(stressed_cash)

    return ReplayReport(
        path_results=baseline_results,
        flat_count=flat_count,
        total_paths=len(paths),
        hit_target_count=hit_target_count,
        stressed_path_results=stressed_results,
    )
