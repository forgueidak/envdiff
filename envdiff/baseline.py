"""Baseline snapshot management: save and load a .env diff baseline for change tracking."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from envdiff.comparator import DiffResult


_BASELINE_VERSION = 1


def _result_to_dict(result: DiffResult) -> Dict[str, Any]:
    return {
        "missing_in_target": list(result.missing_in_target),
        "missing_in_base": list(result.missing_in_base),
        "mismatched": {
            k: {"base": v[0], "target": v[1]}
            for k, v in result.mismatched.items()
        },
    }


def _dict_to_result(data: Dict[str, Any]) -> DiffResult:
    mismatched = {
        k: (v["base"], v["target"])
        for k, v in data.get("mismatched", {}).items()
    }
    return DiffResult(
        missing_in_target=set(data.get("missing_in_target", [])),
        missing_in_base=set(data.get("missing_in_base", [])),
        mismatched=mismatched,
    )


def save_baseline(result: DiffResult, path: str | Path) -> None:
    """Persist a DiffResult as a JSON baseline file."""
    payload = {
        "version": _BASELINE_VERSION,
        "diff": _result_to_dict(result),
    }
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_baseline(path: str | Path) -> DiffResult:
    """Load a previously saved baseline and return a DiffResult."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if raw.get("version") != _BASELINE_VERSION:
        raise ValueError(
            f"Unsupported baseline version: {raw.get('version')}"
        )
    return _dict_to_result(raw["diff"])


def diff_against_baseline(
    current: DiffResult, baseline: DiffResult
) -> DiffResult:
    """Return only the *new* issues introduced since the baseline."""
    new_missing_target = current.missing_in_target - baseline.missing_in_target
    new_missing_base = current.missing_in_base - baseline.missing_in_base
    new_mismatched = {
        k: v
        for k, v in current.mismatched.items()
        if k not in baseline.mismatched
    }
    return DiffResult(
        missing_in_target=new_missing_target,
        missing_in_base=new_missing_base,
        mismatched=new_mismatched,
    )
