"""Support for comparing multiple target .env files against a single base."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from envdiff.comparator import compare_envs
from envdiff.parser import parse_env_file
from envdiff.sorter import GroupedDiff, group_by_label, merge_groups


def compare_many(
    base_path: str | Path,
    target_paths: List[str | Path],
    mask_secrets: bool = False,
    labels: Optional[List[str]] = None,
) -> Dict[str, GroupedDiff]:
    """Compare *base_path* against each file in *target_paths*.

    Parameters
    ----------
    base_path:
        The reference .env file.
    target_paths:
        One or more target .env files to compare against the base.
    mask_secrets:
        When *True*, secret values are replaced with ``***``.
    labels:
        Optional human-readable labels for each target file.  Defaults to
        the file name of each target path.

    Returns
    -------
    dict
        Mapping of label -> :class:`~envdiff.sorter.GroupedDiff`.
    """
    if labels is not None and len(labels) != len(target_paths):
        raise ValueError(
            f"labels length ({len(labels)}) must match "
            f"target_paths length ({len(target_paths)})"
        )

    base_env = parse_env_file(base_path)
    groups: List[GroupedDiff] = []

    for idx, target_path in enumerate(target_paths):
        label = labels[idx] if labels else Path(target_path).name
        target_env = parse_env_file(target_path)
        diff = compare_envs(base_env, target_env, mask_secrets=mask_secrets)
        groups.append(group_by_label(label, diff))

    return merge_groups(groups)


def any_differences(grouped: Dict[str, GroupedDiff]) -> bool:
    """Return *True* if any group contains at least one issue."""
    return any(g.total_issues > 0 for g in grouped.values())
