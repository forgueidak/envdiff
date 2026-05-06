"""Redactor: produce a sanitised copy of a parsed env dict.

All keys that are considered secrets (via the same heuristic used by
the comparator) have their values replaced with a configurable
placeholder so the result can be safely logged or exported.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from envdiff.comparator import _is_secret

DEFAULT_PLACEHOLDER = "***"


@dataclass
class RedactedEnv:
    """A sanitised view of a parsed .env mapping."""

    original_keys: list[str] = field(default_factory=list)
    redacted: Dict[str, str] = field(default_factory=dict)
    redacted_keys: list[str] = field(default_factory=list)

    @property
    def total_keys(self) -> int:
        return len(self.original_keys)

    @property
    def total_redacted(self) -> int:
        return len(self.redacted_keys)


def redact(
    env: Dict[str, str],
    placeholder: str = DEFAULT_PLACEHOLDER,
    extra_patterns: Optional[list[str]] = None,
) -> RedactedEnv:
    """Return a :class:`RedactedEnv` with secret values replaced.

    Parameters
    ----------
    env:
        Parsed key/value mapping (e.g. from ``parse_env_file``).
    placeholder:
        String to substitute for secret values.
    extra_patterns:
        Additional case-insensitive substrings that mark a key as secret
        (supplements the built-in heuristic in :func:`_is_secret`).
    """
    extra_patterns = [p.lower() for p in (extra_patterns or [])]
    redacted: Dict[str, str] = {}
    redacted_keys: list[str] = []

    for key, value in env.items():
        key_lower = key.lower()
        is_extra = any(pat in key_lower for pat in extra_patterns)
        if _is_secret(key) or is_extra:
            redacted[key] = placeholder
            redacted_keys.append(key)
        else:
            redacted[key] = value

    return RedactedEnv(
        original_keys=list(env.keys()),
        redacted=redacted,
        redacted_keys=redacted_keys,
    )


def redact_many(
    envs: Dict[str, Dict[str, str]],
    placeholder: str = DEFAULT_PLACEHOLDER,
    extra_patterns: Optional[list[str]] = None,
) -> Dict[str, RedactedEnv]:
    """Apply :func:`redact` to a mapping of *label -> env dict*."""
    return {
        label: redact(env, placeholder=placeholder, extra_patterns=extra_patterns)
        for label, env in envs.items()
    }
