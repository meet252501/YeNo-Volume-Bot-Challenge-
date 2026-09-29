"""
CLI entry point for running the replay backtest.

Usage:
    python scripts/run_backtest.py --replay-dir data/replay --report out/backtest-report.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.backtest.replay import run_full_replay  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay-dir", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    report = run_full_replay(Path(args.replay_dir))
    print(report.summary())

    out_path = Path(args.report)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {
                "median": report.median,
                "best": report.best,
                "worst": report.worst,
                "flat_rate_pct": report.flat_rate_pct,
                "hit_target_rate_pct": report.hit_target_rate_pct,
                "path_results": report.path_results,
                "stressed_path_results": report.stressed_path_results,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
