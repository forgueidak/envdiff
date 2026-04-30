"""Pipeline builder: chain multiple diff runs across an ordered list of environments."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envdiff.differ import DiffOptions, DiffRun, run_diff


@dataclass
class PipelineResult:
    """Aggregated results for a chain of environment comparisons."""

    runs: List[DiffRun] = field(default_factory=list)

    @property
    def any_issues(self) -> bool:
        return any(r.summary.has_issues() for r in self.runs)

    @property
    def issue_counts(self) -> Dict[str, int]:
        return {
            f"{r.base_path.name} -> {r.target_path.name}": r.summary.total_issues()
            for r in self.runs
        }

    def as_dict(self) -> dict:
        return {
            "any_issues": self.any_issues,
            "runs": [
                {
                    "base": str(r.base_path),
                    "target": str(r.target_path),
                    "total_issues": r.summary.total_issues(),
                    "summary": r.summary.as_dict(),
                }
                for r in self.runs
            ],
        }


def run_pipeline(
    env_paths: List[str | Path],
    options: DiffOptions | None = None,
) -> PipelineResult:
    """Compare each consecutive pair of env files in *env_paths*.

    Given [a, b, c] this produces runs for (a→b) and (b→c).
    """
    if len(env_paths) < 2:
        raise ValueError("At least two environment paths are required for a pipeline.")

    if options is None:
        options = DiffOptions()

    result = PipelineResult()
    paths = [Path(p) for p in env_paths]

    for base, target in zip(paths, paths[1:]):
        diff_run = run_diff(base, target, options=options)
        result.runs.append(diff_run)

    return result
