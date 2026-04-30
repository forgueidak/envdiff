"""High-level summary statistics for one or more diff results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.comparator import DiffResult


@dataclass
class DiffSummary:
    """Aggregated statistics across one or more :class:`~envdiff.comparator.DiffResult` objects."""

    total_missing_in_target: int = 0
    total_missing_in_base: int = 0
    total_mismatched: int = 0
    file_count: int = 0
    files_with_issues: List[str] = field(default_factory=list)

    @property
    def total_issues(self) -> int:
        return self.total_missing_in_target + self.total_missing_in_base + self.total_mismatched

    @property
    def has_issues(self) -> bool:
        return self.total_issues > 0

    def as_dict(self) -> Dict[str, object]:
        return {
            "file_count": self.file_count,
            "files_with_issues": self.files_with_issues,
            "total_missing_in_target": self.total_missing_in_target,
            "total_missing_in_base": self.total_missing_in_base,
            "total_mismatched": self.total_mismatched,
            "total_issues": self.total_issues,
        }


def summarise(result: DiffResult, label: str = "") -> DiffSummary:
    """Build a :class:`DiffSummary` from a single *result*."""
    issues = len(result.missing_in_target) + len(result.missing_in_base) + len(result.mismatched)
    return DiffSummary(
        total_missing_in_target=len(result.missing_in_target),
        total_missing_in_base=len(result.missing_in_base),
        total_mismatched=len(result.mismatched),
        file_count=1,
        files_with_issues=[label] if (issues and label) else [],
    )


def summarise_many(results: Dict[str, DiffResult]) -> DiffSummary:
    """Aggregate multiple labelled results into one :class:`DiffSummary`.

    Parameters
    ----------
    results:
        Mapping of label → :class:`~envdiff.comparator.DiffResult`.
    """
    agg = DiffSummary(file_count=len(results))
    for label, result in results.items():
        agg.total_missing_in_target += len(result.missing_in_target)
        agg.total_missing_in_base += len(result.missing_in_base)
        agg.total_mismatched += len(result.mismatched)
        if result.missing_in_target or result.missing_in_base or result.mismatched:
            agg.files_with_issues.append(label)
    return agg


def format_summary(summary: DiffSummary) -> str:
    """Return a human-readable one-block summary string."""
    lines = [
        f"Files compared : {summary.file_count}",
        f"Files with issues: {len(summary.files_with_issues)}",
        f"Missing in target: {summary.total_missing_in_target}",
        f"Missing in base  : {summary.total_missing_in_base}",
        f"Mismatched keys  : {summary.total_mismatched}",
        f"Total issues     : {summary.total_issues}",
    ]
    if summary.files_with_issues:
        lines.append("Affected files   : " + ", ".join(summary.files_with_issues))
    return "\n".join(lines)
