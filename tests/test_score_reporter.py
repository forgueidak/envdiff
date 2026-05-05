"""Tests for envdiff.score_reporter."""
import json

import pytest

from envdiff.scorer import DiffScore
from envdiff.score_reporter import format_score, _progress_bar


@pytest.fixture()
def perfect() -> DiffScore:
    return DiffScore(score=100, penalty=0, grade="A", total_issues=0)


@pytest.fixture()
def poor() -> DiffScore:
    return DiffScore(score=40, penalty=60, grade="F", total_issues=20)


# --- progress bar -----------------------------------------------------------

def test_progress_bar_full():
    bar = _progress_bar(100)
    assert bar == "[" + "#" * 20 + "-" * 0 + "]"


def test_progress_bar_empty():
    bar = _progress_bar(0)
    assert bar == "[" + "-" * 20 + "]"


def test_progress_bar_half():
    bar = _progress_bar(50)
    assert "#" * 10 in bar


# --- text format ------------------------------------------------------------

def test_text_contains_score(perfect):
    out = format_score(perfect, fmt="text")
    assert "100/100" in out


def test_text_contains_grade(perfect):
    out = format_score(perfect, fmt="text")
    assert "Grade A" in out


def test_text_healthy_label(perfect):
    out = format_score(perfect, fmt="text")
    assert "healthy" in out


def test_text_needs_attention_label(poor):
    out = format_score(poor, fmt="text")
    assert "needs attention" in out


def test_text_total_issues(poor):
    out = format_score(poor, fmt="text")
    assert "20" in out


def test_text_penalty_shown(poor):
    out = format_score(poor, fmt="text")
    assert "60" in out


# --- json format ------------------------------------------------------------

def test_json_is_valid_json(perfect):
    raw = format_score(perfect, fmt="json")
    data = json.loads(raw)
    assert isinstance(data, dict)


def test_json_has_required_keys(perfect):
    data = json.loads(format_score(perfect, fmt="json"))
    assert {"score", "grade", "is_healthy", "total_issues", "penalty"} <= data.keys()


def test_json_score_value(perfect):
    data = json.loads(format_score(perfect, fmt="json"))
    assert data["score"] == 100


def test_json_is_healthy_true(perfect):
    data = json.loads(format_score(perfect, fmt="json"))
    assert data["is_healthy"] is True


def test_json_is_healthy_false(poor):
    data = json.loads(format_score(poor, fmt="json"))
    assert data["is_healthy"] is False


def test_default_format_is_text(perfect):
    out = format_score(perfect)
    assert "Health Score" in out
