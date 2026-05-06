"""Drift detection: compare a live env snapshot against a saved baseline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envdiff.baseline import load_baseline, save_baseline
from envdiff.comparator import DiffResult, compare_envs
from envdiff.parser import parse_env_file


@dataclass
class DriftReport:
    """Result of a drift detection run."""

    baseline_path: str
    env_path: str
    diff: DiffResult
    drifted: bool = field(init=False)

    def __post_init__(self) -> None:
        self.drifted = (
            bool(self.diff.missing_in_target)
            or bool(self.diff.missing_in_base)
            or bool(self.diff.mismatched)
        )

    def summary(self) -> str:
        if not self.drifted:
            return "No drift detected."
        parts: list[str] = []
        if self.diff.missing_in_target:
            parts.append(
                f"{len(self.diff.missing_in_target)} key(s) removed since baseline"
            )
        if self.diff.missing_in_base:
            parts.append(
                f"{len(self.diff.missing_in_base)} key(s) added since baseline"
            )
        if self.diff.mismatched:
            parts.append(
                f"{len(self.diff.mismatched)} key(s) changed since baseline"
            )
        return "Drift detected: " + "; ".join(parts) + "."


def detect_drift(
    env_path: str | Path,
    baseline_path: str | Path,
    mask_secrets: bool = False,
) -> DriftReport:
    """Compare *env_path* against a previously saved *baseline_path*.

    The baseline stores a DiffResult snapshot (see :mod:`envdiff.baseline`).
    We reload the baseline's embedded env values and diff them against the
    current file so that added/removed/changed keys are all surfaced.
    """
    baseline_result: DiffResult = load_baseline(str(baseline_path))

    # Reconstruct the "baseline env" from the union of keys known at save time.
    baseline_env: dict[str, str] = {}
    for key in baseline_result.missing_in_target:
        baseline_env[key] = ""
    for key, (base_val, _) in baseline_result.mismatched.items():
        baseline_env[key] = base_val
    # Keys that were only in base at snapshot time
    for key in baseline_result.missing_in_base:
        baseline_env[key] = ""

    current_env: dict[str, str] = parse_env_file(str(env_path))

    diff = compare_envs(baseline_env, current_env, mask_secrets=mask_secrets)
    return DriftReport(
        baseline_path=str(baseline_path),
        env_path=str(env_path),
        diff=diff,
    )


def update_baseline(
    env_path: str | Path,
    baseline_path: str | Path,
) -> None:
    """Overwrite *baseline_path* with a fresh snapshot of *env_path*."""
    current_env = parse_env_file(str(env_path))
    empty: dict[str, str] = {}
    fresh_diff = compare_envs(current_env, empty, mask_secrets=False)
    save_baseline(fresh_diff, str(baseline_path))
