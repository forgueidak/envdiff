"""Comparator module for envdiff — compares parsed env file dictionaries."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class DiffResult:
    """Holds the result of comparing two env files."""

    base_name: str
    target_name: str
    missing_in_target: List[str] = field(default_factory=list)
    missing_in_base: List[str] = field(default_factory=list)
    mismatched: Dict[str, Dict[str, Optional[str]]] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(self.missing_in_target or self.missing_in_base or self.mismatched)


def compare_envs(
    base: Dict[str, str],
    target: Dict[str, str],
    base_name: str = "base",
    target_name: str = "target",
    mask_secrets: bool = False,
    secret_keywords: Optional[List[str]] = None,
) -> DiffResult:
    """Compare two env dictionaries and return a DiffResult.

    Args:
        base: The reference env dictionary.
        target: The env dictionary to compare against base.
        base_name: Label for the base environment.
        target_name: Label for the target environment.
        mask_secrets: If True, mask values for keys matching secret_keywords.
        secret_keywords: List of substrings that indicate a secret key.

    Returns:
        A DiffResult describing the differences.
    """
    if secret_keywords is None:
        secret_keywords = ["secret", "password", "passwd", "token", "key", "api_key"]

    base_keys: Set[str] = set(base.keys())
    target_keys: Set[str] = set(target.keys())

    result = DiffResult(base_name=base_name, target_name=target_name)
    result.missing_in_target = sorted(base_keys - target_keys)
    result.missing_in_base = sorted(target_keys - base_keys)

    common_keys = base_keys & target_keys
    for key in sorted(common_keys):
        base_val = base[key]
        target_val = target[key]
        if base_val != target_val:
            if mask_secrets and _is_secret(key, secret_keywords):
                base_val = "***"
                target_val = "***"
            result.mismatched[key] = {base_name: base_val, target_name: target_val}

    return result


def _is_secret(key: str, secret_keywords: List[str]) -> bool:
    """Return True if the key contains any secret keyword (case-insensitive)."""
    lower_key = key.lower()
    return any(kw in lower_key for kw in secret_keywords)
