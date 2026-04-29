"""Tests for envdiff.reporter module."""

import json
import pytest
from envdiff.comparator import DiffResult
from envdiff.reporter import format_report


@pytest.fixture
def full_result():
    return DiffResult(
        missing_in_target={"DB_HOST"},
        missing_in_base={"NEW_FEATURE_FLAG"},
        mismatched={"APP_ENV": ("development", "production")},
    )


@pytest.fixture
def empty_result():
    return DiffResult(missing_in_target=set(), missing_in_base=set(), mismatched={})


# --- Text format ---

def test_text_missing_in_target(full_result):
    report = format_report(full_result, fmt="text")
    assert "Missing in target:" in report
    assert "  - DB_HOST" in report


def test_text_missing_in_base(full_result):
    report = format_report(full_result, fmt="text")
    assert "Missing in base:" in report
    assert "  + NEW_FEATURE_FLAG" in report


def test_text_mismatched(full_result):
    report = format_report(full_result, fmt="text")
    assert "Mismatched values:" in report
    assert "  ~ APP_ENV" in report
    assert "development" in report
    assert "production" in report


def test_text_no_differences(empty_result):
    report = format_report(empty_result, fmt="text")
    assert report == "No differences found."


def test_text_is_default_format(full_result):
    assert format_report(full_result) == format_report(full_result, fmt="text")


# --- JSON format ---

def test_json_format_is_valid_json(full_result):
    report = format_report(full_result, fmt="json")
    data = json.loads(report)
    assert isinstance(data, dict)


def test_json_contains_expected_keys(full_result):
    data = json.loads(format_report(full_result, fmt="json"))
    assert "missing_in_target" in data
    assert "missing_in_base" in data
    assert "mismatched" in data


def test_json_missing_in_target(full_result):
    data = json.loads(format_report(full_result, fmt="json"))
    assert "DB_HOST" in data["missing_in_target"]


def test_json_mismatched_structure(full_result):
    data = json.loads(format_report(full_result, fmt="json"))
    assert data["mismatched"]["APP_ENV"] == {"base": "development", "target": "production"}


def test_json_empty_result(empty_result):
    data = json.loads(format_report(empty_result, fmt="json"))
    assert data["missing_in_target"] == []
    assert data["missing_in_base"] == []
    assert data["mismatched"] == {}


# --- Markdown format ---

def test_markdown_contains_heading(full_result):
    report = format_report(full_result, fmt="markdown")
    assert "# Env Diff Report" in report


def test_markdown_missing_in_target(full_result):
    report = format_report(full_result, fmt="markdown")
    assert "## Missing in Target" in report
    assert "`DB_HOST`" in report


def test_markdown_none_when_empty(empty_result):
    report = format_report(empty_result, fmt="markdown")
    assert report.count("_None_") == 3


def test_markdown_mismatched_arrow(full_result):
    report = format_report(full_result, fmt="markdown")
    assert "→" in report
