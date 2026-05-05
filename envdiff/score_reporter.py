"""Formats a DiffScore for human-readable or JSON output."""
from __future__ import annotations

import json
from typing import Literal

from envdiff.scorer import DiffScore

OutputFormat = Literal["text", "json"]

_BAR_WIDTH = 20


def _progress_bar(score: int, width: int = _BAR_WIDTH) -> str:
    filled = round(score / 100 * width)
    empty = width - filled
    return "[" + "#" * filled + "-" * empty + "]"


def format_score(ds: DiffScore, fmt: OutputFormat = "text") -> str:
    """Return a formatted string representation of *ds*.

    Parameters
    ----------
    ds:
        The score to format.
    fmt:
        ``"text"`` (default) or ``"json"``.
    """
    if fmt == "json":
        return _format_json(ds)
    return _format_text(ds)


def _format_text(ds: DiffScore) -> str:
    bar = _progress_bar(ds.score)
    healthy = "✓ healthy" if ds.is_healthy else "✗ needs attention"
    lines = [
        f"Health Score : {ds.score}/100  {bar}  Grade {ds.grade}",
        f"Status       : {healthy}",
        f"Total issues : {ds.total_issues}",
        f"Raw penalty  : {ds.penalty}",
    ]
    return "\n".join(lines)


def _format_json(ds: DiffScore) -> str:
    payload = {
        "score": ds.score,
        "grade": ds.grade,
        "is_healthy": ds.is_healthy,
        "total_issues": ds.total_issues,
        "penalty": ds.penalty,
    }
    return json.dumps(payload, indent=2)
