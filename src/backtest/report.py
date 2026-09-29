"""Replay report shape — matches Builderr's own published benchmark format."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReplayReport:
    path_results: list[float]
    flat_count: int
    total_paths: int
    hit_target_count: int
    stressed_path_results: list[float]

    @property
    def median(self) -> float:
        s = sorted(self.path_results)
        n = len(s)
        return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2

    @property
    def best(self) -> float:
        return max(self.path_results) if self.path_results else 0.0

    @property
    def worst(self) -> float:
        return min(self.path_results) if self.path_results else 0.0

    @property
    def flat_rate_pct(self) -> float:
        return 100 * self.flat_count / self.total_paths if self.total_paths else 0.0

    @property
    def hit_target_rate_pct(self) -> float:
        return 100 * self.hit_target_count / self.total_paths if self.total_paths else 0.0

    def summary(self) -> str:
        return (
            f"median=${self.median:.2f} best=${self.best:.2f} worst=${self.worst:.2f} "
            f"flat={self.flat_rate_pct:.0f}% hit_target={self.hit_target_rate_pct:.0f}%"
        )
