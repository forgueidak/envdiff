"""Point-in-time snapshot of an environment file with metadata."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from envdiff.parser import parse_env_file


@dataclass
class EnvSnapshot:
    path: str
    captured_at: str
    keys: Dict[str, str]
    checksum: str
    label: Optional[str] = None

    # ------------------------------------------------------------------ #
    def __len__(self) -> int:
        return len(self.keys)

    def key_count(self) -> int:
        return len(self.keys)

    def as_dict(self) -> dict:
        return {
            "path": self.path,
            "captured_at": self.captured_at,
            "label": self.label,
            "checksum": self.checksum,
            "key_count": self.key_count(),
            "keys": self.keys,
        }


def _checksum(data: Dict[str, str]) -> str:
    """Stable SHA-256 of the sorted key=value pairs."""
    payload = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    return hashlib.sha256(payload.encode()).hexdigest()


def capture(path: str, label: Optional[str] = None) -> EnvSnapshot:
    """Parse *path* and return a timestamped snapshot."""
    keys = parse_env_file(path)
    return EnvSnapshot(
        path=path,
        captured_at=datetime.now(timezone.utc).isoformat(),
        keys=keys,
        checksum=_checksum(keys),
        label=label,
    )


def save_snapshot(snapshot: EnvSnapshot, dest: str) -> None:
    """Persist *snapshot* to *dest* as JSON."""
    Path(dest).write_text(json.dumps(snapshot.as_dict(), indent=2))


def load_snapshot(src: str) -> EnvSnapshot:
    """Load a previously saved snapshot from *src*."""
    raw = json.loads(Path(src).read_text())
    return EnvSnapshot(
        path=raw["path"],
        captured_at=raw["captured_at"],
        keys=raw["keys"],
        checksum=raw["checksum"],
        label=raw.get("label"),
    )


def snapshots_equal(a: EnvSnapshot, b: EnvSnapshot) -> bool:
    """Return True when both snapshots have identical content (same checksum)."""
    return a.checksum == b.checksum
