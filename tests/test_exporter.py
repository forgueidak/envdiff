"""Tests for envdiff.exporter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.comparator import DiffResult
from envdiff.exporter import export_result, export_to_file, SUPPORTED_FORMATS


@pytest.fixture()
def sample_result() -> DiffResult:
    return DiffResult(
        missing_in_target={"ALPHA"},
        missing_in_base={"BETA"},
        mismatched={"GAMMA": ("old", "new"), "SECRET_KEY": ("abc", "xyz")},
        masked_keys={"SECRET_KEY"},
    )


# ---------------------------------------------------------------------------
# format validation
# ---------------------------------------------------------------------------

def test_unsupported_format_raises(sample_result):
    with pytest.raises(ValueError, match="Unsupported format"):
        export_result(sample_result, fmt="xml")


def test_supported_formats_constant():
    assert "json" in SUPPORTED_FORMATS
    assert "csv" in SUPPORTED_FORMATS
    assert "markdown" in SUPPORTED_FORMATS


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------

def test_json_export_is_valid_json(sample_result):
    output = export_result(sample_result, fmt="json")
    data = json.loads(output)
    assert "missing_in_target" in data
    assert "ALPHA" in data["missing_in_target"]


def test_json_export_masks_secrets(sample_result):
    output = export_result(sample_result, fmt="json", mask_secrets=True)
    data = json.loads(output)
    assert data["mismatched"]["SECRET_KEY"] == ["***", "***"]


# ---------------------------------------------------------------------------
# Markdown export
# ---------------------------------------------------------------------------

def test_markdown_export_contains_headings(sample_result):
    output = export_result(sample_result, fmt="markdown")
    assert "#" in output


def test_markdown_export_contains_key(sample_result):
    output = export_result(sample_result, fmt="markdown")
    assert "ALPHA" in output


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

def test_csv_export_has_header(sample_result):
    output = export_result(sample_result, fmt="csv")
    assert output.startswith("type,key,base_value,target_value")


def test_csv_export_missing_in_target_row(sample_result):
    output = export_result(sample_result, fmt="csv")
    assert "missing_in_target,ALPHA" in output


def test_csv_export_missing_in_base_row(sample_result):
    output = export_result(sample_result, fmt="csv")
    assert "missing_in_base,BETA" in output


def test_csv_export_mismatched_row(sample_result):
    output = export_result(sample_result, fmt="csv")
    assert "mismatched,GAMMA,old,new" in output


def test_csv_export_masks_secrets(sample_result):
    output = export_result(sample_result, fmt="csv", mask_secrets=True)
    assert "mismatched,SECRET_KEY,***,***" in output
    assert "abc" not in output


# ---------------------------------------------------------------------------
# File export
# ---------------------------------------------------------------------------

def test_export_to_file_writes_content(tmp_path, sample_result):
    dest = tmp_path / "report.json"
    returned = export_to_file(sample_result, dest)
    assert returned == dest
    assert dest.exists()
    data = json.loads(dest.read_text())
    assert "missing_in_target" in data


def test_export_to_file_infers_markdown_extension(tmp_path, sample_result):
    dest = tmp_path / "report.md"
    export_to_file(sample_result, dest)
    content = dest.read_text()
    assert "#" in content


def test_export_to_file_infers_csv_extension(tmp_path, sample_result):
    dest = tmp_path / "report.csv"
    export_to_file(sample_result, dest)
    content = dest.read_text()
    assert content.startswith("type,key")


def test_export_to_file_explicit_fmt_overrides_extension(tmp_path, sample_result):
    dest = tmp_path / "output.txt"
    export_to_file(sample_result, dest, fmt="csv")
    content = dest.read_text()
    assert content.startswith("type,key")
