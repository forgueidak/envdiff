"""Merge multiple .env files into a single resolved environment map.

Later files take precedence over earlier ones (last-write-wins).
Optionally reports which keys were overridden and by which source.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from envdiff.parser import parse_env_file


@dataclass
class MergeConflict:
    """Records a key that was overridden during a merge."""
    key: str
    original_value: str
    original_source: str
    winning_value: str
    winning_source: str

    def __str__(self) -> str:  # pragma: no cover
        return (
            f"{self.key}: '{self.original_value}' ({self.original_source}) "
            f"-> '{self.winning_value}' ({self.winning_source})"
        )


@dataclass
class MergeResult:
    """The outcome of merging two or more .env files."""
    merged: Dict[str, str]
    conflicts: List[MergeConflict] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    @property
    def conflict_count(self) -> int:
        return len(self.conflicts)

    def as_dict(self) -> dict:
        return {
            "sources": self.sources,
            "merged": self.merged,
            "conflicts": [
                {
                    "key": c.key,
                    "original_value": c.original_value,
                    "original_source": c.original_source,
                    "winning_value": c.winning_value,
                    "winning_source": c.winning_source,
                }
                for c in self.conflicts
            ],
        }


def merge_env_files(
    paths: List[Path],
    *,
    labels: Optional[List[str]] = None,
) -> MergeResult:
    """Merge env files in order; later files win on key conflicts.

    Args:
        paths: Ordered list of .env file paths.
        labels: Optional human-readable labels for each path.

    Returns:
        A :class:`MergeResult` with the resolved map and any conflicts.
    """
    if len(paths) < 2:
        raise ValueError("merge_env_files requires at least two paths.")

    resolved_labels = [
        (labels[i] if labels and i < len(labels) else str(p))
        for i, p in enumerate(paths)
    ]

    merged: Dict[str, str] = {}
    key_source: Dict[str, Tuple[str, str]] = {}  # key -> (value, label)
    conflicts: List[MergeConflict] = []

    for label, path in zip(resolved_labels, paths):
        env = parse_env_file(path)
        for key, value in env.items():
            if key in key_source:
                prev_value, prev_label = key_source[key]
                if prev_value != value:
                    conflicts.append(
                        MergeConflict(
                            key=key,
                            original_value=prev_value,
                            original_source=prev_label,
                            winning_value=value,
                            winning_source=label,
                        )
                    )
            merged[key] = value
            key_source[key] = (value, label)

    return MergeResult(
        merged=merged,
        conflicts=conflicts,
        sources=resolved_labels,
    )
