"""Detect deprecated or renamed keys across .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DeprecationRule:
    """A rule mapping an old key name to its replacement (if any)."""

    old_key: str
    new_key: Optional[str] = None
    reason: Optional[str] = None

    def message(self) -> str:
        parts = [f"'{self.old_key}' is deprecated"]
        if self.new_key:
            parts.append(f"use '{self.new_key}' instead")
        if self.reason:
            parts.append(f"({self.reason})")
        return "; ".join(parts) if len(parts) > 1 else parts[0]


@dataclass
class DeprecationHit:
    """A single detected use of a deprecated key."""

    key: str
    rule: DeprecationRule

    def __str__(self) -> str:
        return f"[DEPRECATED] {self.rule.message()}"


@dataclass
class DeprecationReport:
    """Result of scanning an env mapping for deprecated keys."""

    hits: List[DeprecationHit] = field(default_factory=list)
    scanned_keys: int = 0

    @property
    def has_hits(self) -> bool:
        return bool(self.hits)

    @property
    def hit_count(self) -> int:
        return len(self.hits)

    def as_dict(self) -> dict:
        return {
            "scanned_keys": self.scanned_keys,
            "hit_count": self.hit_count,
            "hits": [
                {
                    "key": h.key,
                    "new_key": h.rule.new_key,
                    "reason": h.rule.reason,
                    "message": str(h),
                }
                for h in self.hits
            ],
        }


def check_deprecations(
    env: Dict[str, str],
    rules: List[DeprecationRule],
) -> DeprecationReport:
    """Scan *env* for keys that match any deprecation rule."""
    rule_index: Dict[str, DeprecationRule] = {r.old_key: r for r in rules}
    hits: List[DeprecationHit] = []

    for key in env:
        if key in rule_index:
            hits.append(DeprecationHit(key=key, rule=rule_index[key]))

    return DeprecationReport(hits=hits, scanned_keys=len(env))
