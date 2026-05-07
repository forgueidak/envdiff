"""Tracks and formats a changelog of env diff runs over time."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from envdiff.comparator import DiffResult


@dataclass
class ChangelogEntry:
    timestamp: str
    base: str
    target: str
    missing_in_target: List[str]
    missing_in_base: List[str]
    mismatched: List[str]

    @property
    def total_issues(self) -> int:
        return (
            len(self.missing_in_target)
            + len(self.missing_in_base)
            + len(self.mismatched)
        )

    def as_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "base": self.base,
            "target": self.target,
            "missing_in_target": self.missing_in_target,
            "missing_in_base": self.missing_in_base,
            "mismatched": self.mismatched,
            "total_issues": self.total_issues,
        }


@dataclass
class Changelog:
    entries: List[ChangelogEntry] = field(default_factory=list)

    def add(self, entry: ChangelogEntry) -> None:
        self.entries.append(entry)

    def __len__(self) -> int:
        return len(self.entries)

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_entry(
    result: DiffResult,
    base_label: str,
    target_label: str,
    timestamp: Optional[str] = None,
) -> ChangelogEntry:
    """Create a ChangelogEntry from a DiffResult."""
    return ChangelogEntry(
        timestamp=timestamp or _now_iso(),
        base=base_label,
        target=target_label,
        missing_in_target=sorted(result.missing_in_target),
        missing_in_base=sorted(result.missing_in_base),
        mismatched=sorted(result.mismatched.keys()),
    )


def save_changelog(changelog: Changelog, path: Path) -> None:
    """Persist a Changelog to a JSON file."""
    path.write_text(json.dumps(changelog.as_dict(), indent=2))


def load_changelog(path: Path) -> Changelog:
    """Load a Changelog from a JSON file."""
    data = json.loads(path.read_text())
    entries = [
        ChangelogEntry(
            timestamp=e["timestamp"],
            base=e["base"],
            target=e["target"],
            missing_in_target=e["missing_in_target"],
            missing_in_base=e["missing_in_base"],
            mismatched=e["mismatched"],
        )
        for e in data.get("entries", [])
    ]
    return Changelog(entries=entries)
