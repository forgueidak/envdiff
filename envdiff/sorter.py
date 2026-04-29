"""Utilities for sorting and grouping diff results by category."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.comparator import DiffResult


@dataclass
class GroupedDiff:
    """Diff results organised into named groups (e.g. per-environment label)."""

    label: str
    missing_in_target: List[str] = field(default_factory=list)
    missing_in_base: List[str] = field(default_factory=list)
    mismatched: Dict[str, Dict[str, str]] = field(default_factory=dict)

    @property
    def total_issues(self) -> int:
        return (
            len(self.missing_in_target)
            + len(self.missing_in_base)
            + len(self.mismatched)
        )


def sort_keys(result: DiffResult) -> DiffResult:
    """Return a new DiffResult with all key collections sorted alphabetically."""
    return DiffResult(
        missing_in_target=sorted(result.missing_in_target),
        missing_in_base=sorted(result.missing_in_base),
        mismatched=dict(sorted(result.mismatched.items())),
    )


def group_by_label(label: str, result: DiffResult) -> GroupedDiff:
    """Wrap a DiffResult in a GroupedDiff with the given label."""
    sorted_result = sort_keys(result)
    return GroupedDiff(
        label=label,
        missing_in_target=sorted_result.missing_in_target,
        missing_in_base=sorted_result.missing_in_base,
        mismatched=sorted_result.mismatched,
    )


def merge_groups(groups: List[GroupedDiff]) -> Dict[str, GroupedDiff]:
    """Index a list of GroupedDiff objects by their label for quick lookup."""
    return {g.label: g for g in groups}
