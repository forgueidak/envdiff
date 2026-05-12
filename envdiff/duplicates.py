"""Detect duplicate keys within a single .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class DuplicateReport:
    """Result of a duplicate-key scan on one .env file."""

    path: Path
    duplicates: Dict[str, int] = field(default_factory=dict)
    """Mapping of key -> number of times it appears (only keys with count > 1)."""

    @property
    def has_duplicates(self) -> bool:
        return bool(self.duplicates)

    @property
    def total_duplicate_keys(self) -> int:
        return len(self.duplicates)

    def summary(self) -> str:
        if not self.has_duplicates:
            return f"{self.path}: no duplicate keys"
        lines = [f"{self.path}: {self.total_duplicate_keys} duplicate key(s)"]
        for key, count in sorted(self.duplicates.items()):
            lines.append(f"  {key}: appears {count} times")
        return "\n".join(lines)


def find_duplicates(path: Path | str) -> DuplicateReport:
    """Scan *path* for duplicate keys and return a :class:`DuplicateReport`."""
    path = Path(path)
    counts: Dict[str, int] = {}

    with path.open(encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key = line.split("=", 1)[0].strip()
            if key:
                counts[key] = counts.get(key, 0) + 1

    duplicates = {k: v for k, v in counts.items() if v > 1}
    return DuplicateReport(path=path, duplicates=duplicates)


def find_duplicates_many(paths: List[Path | str]) -> List[DuplicateReport]:
    """Run :func:`find_duplicates` over multiple files."""
    return [find_duplicates(p) for p in paths]


def any_duplicates(reports: List[DuplicateReport]) -> bool:
    """Return ``True`` if at least one report contains duplicates."""
    return any(r.has_duplicates for r in reports)
