"""Normalize .env values for consistent comparison.

Handles common value variations such as differing boolean representations,
whitespace, and numeric formatting so that semantically equal values are
not reported as mismatches.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

# Canonical forms for boolean-like strings
_TRUE_VALUES = {"true", "1", "yes", "on"}
_FALSE_VALUES = {"false", "0", "no", "off"}


@dataclass
class NormalizedEnv:
    """Holds the original and normalized key-value pairs for one env."""

    original: Dict[str, str]
    normalized: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.normalized = {k: normalize_value(v) for k, v in self.original.items()}


def normalize_value(value: str) -> str:
    """Return a canonical form of *value* for comparison purposes.

    Rules applied in order:
    1. Strip surrounding whitespace.
    2. Collapse boolean synonyms to ``"true"`` or ``"false"``.
    3. Normalize numeric strings by stripping leading zeros (integers only).
    """
    stripped = value.strip()
    lower = stripped.lower()

    if lower in _TRUE_VALUES:
        return "true"
    if lower in _FALSE_VALUES:
        return "false"

    # Normalize plain integers (no decimals, no signs beyond leading minus)
    try:
        int_val = int(stripped, 10)
        return str(int_val)
    except (ValueError, TypeError):
        pass

    return stripped


def normalize_many(envs: Dict[str, Dict[str, str]]) -> Dict[str, NormalizedEnv]:
    """Normalize a mapping of *label -> raw env dict* and return NormalizedEnv objects."""
    return {label: NormalizedEnv(original=raw) for label, raw in envs.items()}


def values_equivalent(a: str, b: str) -> bool:
    """Return True when *a* and *b* normalize to the same value."""
    return normalize_value(a) == normalize_value(b)


def find_normalized_mismatches(
    base: Dict[str, str],
    target: Dict[str, str],
    *,
    mask_secrets: bool = False,
) -> Dict[str, Dict[str, Optional[str]]]:
    """Return keys present in both envs whose *normalized* values differ.

    Returns a dict mapping key -> {"base": ..., "target": ...}.
    When *mask_secrets* is True the values are replaced with ``"***"``.
    """
    from envdiff.comparator import _is_secret  # local import to avoid cycles

    shared = set(base) & set(target)
    result: Dict[str, Dict[str, Optional[str]]] = {}
    for key in sorted(shared):
        if not values_equivalent(base[key], target[key]):
            if mask_secrets and _is_secret(key):
                result[key] = {"base": "***", "target": "***"}
            else:
                result[key] = {"base": base[key], "target": target[key]}
    return result
