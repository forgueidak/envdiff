"""Tests for envdiff.scorer."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.scorer import DiffScore, score_diff


def _result(
    missing_in_target=(),
    missing_in_base=(),
    mismatched=(),
) -> DiffResult:
    return DiffResult(
        missing_in_target=list(missing_in_target),
        missing_in_base=list(missing_in_base),
        mismatched={k: v for k, v in mismatched},
    )


def test_perfect_score_when_no_issues():
    result = score_diff(_result())
    assert result.score == 100
    assert result.grade == "A"
    assert result.penalty == 0
    assert result.total_issues == 0
    assert result.is_healthy is True


def test_missing_in_target_applies_weight_3():
    result = score_diff(_result(missing_in_target=["KEY_A"]))
    assert result.penalty == 3
    assert result.score == 97


def test_missing_in_base_applies_weight_2():
    result = score_diff(_result(missing_in_base=["KEY_B"]))
    assert result.penalty == 2
    assert result.score == 98


def test_mismatch_applies_weight_1():
    result = score_diff(_result(mismatched=[("KEY_C", ("v1", "v2"))]))
    assert result.penalty == 1
    assert result.score == 99


def test_combined_penalty_accumulates():
    result = score_diff(
        _result(
            missing_in_target=["A", "B"],
            missing_in_base=["C"],
            mismatched=[("D", ("x", "y")), ("E", ("p", "q"))],
        )
    )
    # 2*3 + 1*2 + 2*1 = 10
    assert result.penalty == 10
    assert result.score == 90
    assert result.total_issues == 5


def test_score_clamped_to_zero_for_massive_penalty():
    keys = [f"KEY_{i}" for i in range(50)]
    result = score_diff(_result(missing_in_target=keys))
    assert result.score == 0


def test_grade_f_when_score_below_50():
    keys = [f"K{i}" for i in range(20)]
    ds = score_diff(_result(missing_in_target=keys))
    assert ds.grade == "F"


def test_grade_b_boundary():
    from envdiff.scorer import _grade
    assert _grade(80) == "B"
    assert _grade(89) == "B"


def test_grade_c_boundary():
    from envdiff.scorer import _grade
    assert _grade(65) == "C"
    assert _grade(79) == "C"


def test_penalty_cap_parameter():
    keys = [f"K{i}" for i in range(10)]
    result = score_diff(_result(missing_in_target=keys), penalty_cap=30)
    # penalty = 30, cap = 30 → score = 0
    assert result.score == 0


def test_is_healthy_false_below_80():
    keys = [f"K{i}" for i in range(8)]
    ds = score_diff(_result(missing_in_target=keys))
    assert ds.is_healthy is False


def test_returns_diff_score_instance():
    ds = score_diff(_result())
    assert isinstance(ds, DiffScore)
