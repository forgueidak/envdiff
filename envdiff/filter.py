"""Key filtering utilities for envdiff.

Allows users to include or exclude specific keys (or glob patterns)
when comparing .env files.
"""

from __future__ import annotations

import fnmatch
from typing import Collection, Dict, Iterable, Optional


def _matches_any(key: str, patterns: Collection[str]) -> bool:
    """Return True if *key* matches any of the given glob *patterns*."""
    return any(fnmatch.fnmatch(key, pattern) for pattern in patterns)


def filter_keys(
    env: Dict[str, str],
    *,
    include: Optional[Collection[str]] = None,
    exclude: Optional[Collection[str]] = None,
) -> Dict[str, str]:
    """Return a filtered copy of *env*.

    Parameters
    ----------
    env:
        The parsed environment mapping to filter.
    include:
        If provided, only keys matching at least one pattern are kept.
        Supports glob wildcards (e.g. ``"DB_*"``).
    exclude:
        If provided, keys matching any pattern are removed.
        Applied *after* ``include``.

    Returns
    -------
    dict
        A new dict containing only the keys that pass both filters.
    """
    result: Dict[str, str] = dict(env)

    if include:
        result = {k: v for k, v in result.items() if _matches_any(k, include)}

    if exclude:
        result = {k: v for k, v in result.items() if not _matches_any(k, exclude)}

    return result


def filter_keys_many(
    envs: Iterable[Dict[str, str]],
    *,
    include: Optional[Collection[str]] = None,
    exclude: Optional[Collection[str]] = None,
) -> list[Dict[str, str]]:
    """Apply :func:`filter_keys` to every mapping in *envs*."""
    return [
        filter_keys(env, include=include, exclude=exclude)
        for env in envs
    ]
