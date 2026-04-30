"""Tests for envdiff.baseline."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.comparator import DiffResult
from envdiff.baseline import (
    save_baseline,
    load_baseline,
    diff_against_baseline,
)


@pytest.fixture()
def sample_result() -> DiffResult:
    return DiffResult(
        missing_in_target={"FOO", "BAR"},
        missing_in_base={"EXTRA"},
        mismatched={"DB_HOST": ("localhost", "prod.db")},
    )


def test_save_creates_file(tmp_path: Path, sample_result: DiffResult) -> None:
    dest = tmp_path / "baseline.json"
    save_baseline(sample_result, dest)
    assert dest.exists()


def test_save_file_is_valid_json(tmp_path: Path, sample_result: DiffResult) -> None:
    dest = tmp_path / "baseline.json"
    save_baseline(sample_result, dest)
    data = json.loads(dest.read_text())
    assert "version" in data
    assert "diff" in data


def test_roundtrip_missing_in_target(tmp_path: Path, sample_result: DiffResult) -> None:
    dest = tmp_path / "baseline.json"
    save_baseline(sample_result, dest)
    loaded = load_baseline(dest)
    assert loaded.missing_in_target == sample_result.missing_in_target


def test_roundtrip_missing_in_base(tmp_path: Path, sample_result: DiffResult) -> None:
    dest = tmp_path / "baseline.json"
    save_baseline(sample_result, dest)
    loaded = load_baseline(dest)
    assert loaded.missing_in_base == sample_result.missing_in_base


def test_roundtrip_mismatched(tmp_path: Path, sample_result: DiffResult) -> None:
    dest = tmp_path / "baseline.json"
    save_baseline(sample_result, dest)
    loaded = load_baseline(dest)
    assert loaded.mismatched == sample_result.mismatched


def test_load_wrong_version_raises(tmp_path: Path) -> None:
    dest = tmp_path / "baseline.json"
    dest.write_text(json.dumps({"version": 99, "diff": {}}))
    with pytest.raises(ValueError, match="Unsupported baseline version"):
        load_baseline(dest)


def test_diff_against_baseline_new_missing(sample_result: DiffResult) -> None:
    baseline = DiffResult(
        missing_in_target={"FOO"},
        missing_in_base=set(),
        mismatched={},
    )
    delta = diff_against_baseline(sample_result, baseline)
    assert delta.missing_in_target == {"BAR"}


def test_diff_against_baseline_no_new_issues(sample_result: DiffResult) -> None:
    delta = diff_against_baseline(sample_result, sample_result)
    assert not delta.missing_in_target
    assert not delta.missing_in_base
    assert not delta.mismatched


def test_diff_against_baseline_new_mismatch(sample_result: DiffResult) -> None:
    baseline = DiffResult(
        missing_in_target=sample_result.missing_in_target,
        missing_in_base=sample_result.missing_in_base,
        mismatched={},
    )
    delta = diff_against_baseline(sample_result, baseline)
    assert "DB_HOST" in delta.mismatched
