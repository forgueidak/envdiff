"""Tests for envdiff.merger_reporter."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envdiff.merger import merge_env_files, MergeResult
from envdiff.merger_reporter import format_merge_report


@pytest.fixture()
def conflict_result(tmp_path) -> MergeResult:
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("KEY=original\nOTHER=shared\n")
    b.write_text("KEY=override\nNEW=added\n")
    return merge_env_files([a, b], labels=["base", "prod"])


@pytest.fixture()
def clean_result(tmp_path) -> MergeResult:
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("A=1\n")
    b.write_text("B=2\n")
    return merge_env_files([a, b], labels=["a", "b"])


# --- text format ---

def test_text_contains_header(conflict_result):
    report = format_merge_report(conflict_result, fmt="text")
    assert "Merge Report" in report


def test_text_shows_conflict_key(conflict_result):
    report = format_merge_report(conflict_result, fmt="text")
    assert "KEY" in report


def test_text_shows_conflict_count(conflict_result):
    report = format_merge_report(conflict_result, fmt="text")
    assert "1" in report


def test_text_no_conflicts_section_when_clean(clean_result):
    report = format_merge_report(clean_result, fmt="text")
    assert "Conflicts:" not in report


# --- json format ---

def test_json_is_valid(conflict_result):
    report = format_merge_report(conflict_result, fmt="json")
    parsed = json.loads(report)
    assert "merged" in parsed
    assert "conflicts" in parsed


def test_json_conflict_entry(conflict_result):
    report = format_merge_report(conflict_result, fmt="json")
    parsed = json.loads(report)
    assert parsed["conflicts"][0]["key"] == "KEY"
    assert parsed["conflicts"][0]["original_value"] == "original"
    assert parsed["conflicts"][0]["winning_value"] == "override"


def test_json_clean_has_empty_conflicts(clean_result):
    report = format_merge_report(clean_result, fmt="json")
    parsed = json.loads(report)
    assert parsed["conflicts"] == []


# --- markdown format ---

def test_markdown_contains_heading(conflict_result):
    report = format_merge_report(conflict_result, fmt="markdown")
    assert "# Merge Report" in report


def test_markdown_contains_conflict_table(conflict_result):
    report = format_merge_report(conflict_result, fmt="markdown")
    assert "| Key |" in report
    assert "`KEY`" in report


def test_markdown_no_table_when_clean(clean_result):
    report = format_merge_report(clean_result, fmt="markdown")
    assert "| Key |" not in report
