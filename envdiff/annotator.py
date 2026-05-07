"""Annotate .env file lines with diff status (missing, mismatched, ok)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult


@dataclass
class AnnotatedLine:
    """A single line from an env file with its diff annotation."""

    key: str
    value: Optional[str]
    status: str  # 'ok' | 'missing_in_target' | 'missing_in_base' | 'mismatched'
    base_value: Optional[str] = None
    target_value: Optional[str] = None

    @property
    def is_ok(self) -> bool:
        return self.status == "ok"


@dataclass
class AnnotatedDiff:
    """Full annotation result for a base/target env pair."""

    base_path: str
    target_path: str
    lines: List[AnnotatedLine] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return any(not ln.is_ok for ln in self.lines)

    def by_status(self, status: str) -> List[AnnotatedLine]:
        return [ln for ln in self.lines if ln.status == status]

    def summary(self) -> Dict[str, int]:
        """Return a count of lines grouped by status.

        Returns:
            A dict mapping each status string to the number of lines with that
            status.  Only statuses that actually appear in ``self.lines`` are
            included.
        """
        counts: Dict[str, int] = {}
        for ln in self.lines:
            counts[ln.status] = counts.get(ln.status, 0) + 1
        return counts


def annotate(
    base: Dict[str, str],
    target: Dict[str, str],
    result: DiffResult,
    base_path: str = "base",
    target_path: str = "target",
) -> AnnotatedDiff:
    """Produce an AnnotatedDiff from parsed env dicts and a DiffResult.

    Args:
        base: Parsed key/value pairs from the base env file.
        target: Parsed key/value pairs from the target env file.
        result: Pre-computed DiffResult for the pair.
        base_path: Label / file path for the base env.
        target_path: Label / file path for the target env.

    Returns:
        AnnotatedDiff with one AnnotatedLine per unique key across both files.
    """
    annotated = AnnotatedDiff(base_path=base_path, target_path=target_path)

    missing_in_target = set(result.missing_in_target)
    missing_in_base = set(result.missing_in_base)
    mismatched_keys = {k for k, *_ in result.mismatched}

    all_keys = sorted(set(base) | set(target))

    for key in all_keys:
        if key in missing_in_target:
            line = AnnotatedLine(
                key=key,
                value=base.get(key),
                status="missing_in_target",
                base_value=base.get(key),
                target_value=None,
            )
        elif key in missing_in_base:
            line = AnnotatedLine(
                key=key,
                value=target.get(key),
                status="missing_in_base",
                base_value=None,
                target_value=target.get(key),
            )
        elif key in mismatched_keys:
            line = AnnotatedLine(
                key=key,
                value=base.get(key),
                status="mismatched",
                base_value=base.get(key),
                target_value=target.get(key),
            )
        else:
            line = AnnotatedLine(
                key=key,
                value=base.get(key),
                status="ok",
                base_value=base.get(key),
                target_value=target.get(key),
            )
        annotated.lines.append(line)

    return annotated
