"""Scores a diff result to give a numeric health indicator for an environment pair."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from envdiff.comparator import DiffResult

# Penalty weights
_WEIGHT_MISSING_IN_TARGET = 3
_WEIGHT_MISSING_IN_BASE = 2
_WEIGHT_MISMATCH = 1

_MAX_SCORE = 100


@dataclass(frozen=True)
class DiffScore:
    """Numeric health score derived from a DiffResult."""

    score: int          # 0 (worst) – 100 (perfect)
    penalty: int        # total raw penalty points
    grade: str          # A / B / C / D / F
    total_issues: int

    @property
    def is_healthy(self) -> bool:
        return self.score >= 80


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 65:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def score_diff(result: DiffResult, penalty_cap: Optional[int] = None) -> DiffScore:
    """Return a DiffScore for *result*.

    Parameters
    ----------
    result:
        The comparison result to evaluate.
    penalty_cap:
        If given, raw penalty is clamped to this value before converting to a
        0-100 score.  Defaults to 100 (so one point of penalty == one point off).
    """
    cap = penalty_cap if penalty_cap is not None else _MAX_SCORE

    raw_penalty = (
        len(result.missing_in_target) * _WEIGHT_MISSING_IN_TARGET
        + len(result.missing_in_base) * _WEIGHT_MISSING_IN_BASE
        + len(result.mismatched) * _WEIGHT_MISMATCH
    )

    clamped = min(raw_penalty, cap)
    score = max(0, _MAX_SCORE - int(clamped * (_MAX_SCORE / cap)))
    total = (
        len(result.missing_in_target)
        + len(result.missing_in_base)
        + len(result.mismatched)
    )

    return DiffScore(
        score=score,
        penalty=raw_penalty,
        grade=_grade(score),
        total_issues=total,
    )
