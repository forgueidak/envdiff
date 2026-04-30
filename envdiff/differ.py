"""High-level diff runner that combines parsing, filtering, comparing, and summarising."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence

from envdiff.comparator import DiffResult, compare_envs
from envdiff.filter import filter_keys
from envdiff.parser import parse_env_file
from envdiff.summary import DiffSummary, summarise


@dataclass
class DiffOptions:
    """Configuration for a single diff run."""

    mask_secrets: bool = True
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    label_base: str = "base"
    label_target: str = "target"


@dataclass
class DiffRun:
    """Result of a complete diff run including metadata."""

    base_path: Path
    target_path: Path
    options: DiffOptions
    result: DiffResult
    summary: DiffSummary


def run_diff(
    base_path: str | Path,
    target_path: str | Path,
    options: Optional[DiffOptions] = None,
) -> DiffRun:
    """Parse, optionally filter, compare two .env files and return a DiffRun."""
    if options is None:
        options = DiffOptions()

    base_path = Path(base_path)
    target_path = Path(target_path)

    base_env = parse_env_file(base_path)
    target_env = parse_env_file(target_path)

    patterns: Sequence[str] = options.include_patterns or []
    excludes: Sequence[str] = options.exclude_patterns or []

    if patterns or excludes:
        base_env = filter_keys(base_env, include=list(patterns), exclude=list(excludes))
        target_env = filter_keys(target_env, include=list(patterns), exclude=list(excludes))

    result = compare_envs(
        base_env,
        target_env,
        mask_secrets=options.mask_secrets,
    )

    diff_summary = summarise(
        result,
        label_base=options.label_base,
        label_target=options.label_target,
    )

    return DiffRun(
        base_path=base_path,
        target_path=target_path,
        options=options,
        result=result,
        summary=diff_summary,
    )
