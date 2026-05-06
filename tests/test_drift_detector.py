"""Tests for envdiff.drift_detector."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.baseline import save_baseline
from envdiff.comparator import DiffResult
from envdiff.drift_detector import DriftReport, detect_drift, update_baseline


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_env(path: Path, content: str) -> None:
    path.write_text(content)


def _make_baseline(tmp_path: Path, diff: DiffResult) -> Path:
    bl = tmp_path / "baseline.json"
    save_baseline(diff, str(bl))
    return bl


# ---------------------------------------------------------------------------
# DriftReport
# ---------------------------------------------------------------------------

def test_drift_report_not_drifted_when_empty_diff(tmp_path):
    diff = DiffResult(missing_in_target=[], missing_in_base=[], mismatched={})
    report = DriftReport(baseline_path="bl.json", env_path=".env", diff=diff)
    assert not report.drifted
    assert report.summary() == "No drift detected."


def test_drift_report_drifted_missing_in_target(tmp_path):
    diff = DiffResult(missing_in_target=["KEY_A"], missing_in_base=[], mismatched={})
    report = DriftReport(baseline_path="bl.json", env_path=".env", diff=diff)
    assert report.drifted
    assert "removed" in report.summary()


def test_drift_report_summary_counts_all_categories():
    diff = DiffResult(
        missing_in_target=["A"],
        missing_in_base=["B", "C"],
        mismatched={"D": ("old", "new")},
    )
    report = DriftReport(baseline_path="bl.json", env_path=".env", diff=diff)
    summary = report.summary()
    assert "1 key(s) removed" in summary
    assert "2 key(s) added" in summary
    assert "1 key(s) changed" in summary


# ---------------------------------------------------------------------------
# detect_drift
# ---------------------------------------------------------------------------

def test_detect_drift_no_drift(tmp_path):
    env_file = tmp_path / ".env"
    _write_env(env_file, "DB_HOST=localhost\nDB_PORT=5432\n")

    # Baseline with no issues (all keys matched)
    diff = DiffResult(missing_in_target=[], missing_in_base=[], mismatched={})
    bl = _make_baseline(tmp_path, diff)

    report = detect_drift(env_file, bl)
    assert not report.drifted


def test_detect_drift_detects_new_key(tmp_path):
    env_file = tmp_path / ".env"
    _write_env(env_file, "DB_HOST=localhost\nNEW_KEY=surprise\n")

    # Baseline only knew about DB_HOST
    diff = DiffResult(
        missing_in_target=["DB_HOST"], missing_in_base=[], mismatched={}
    )
    bl = _make_baseline(tmp_path, diff)

    report = detect_drift(env_file, bl)
    assert report.drifted


def test_detect_drift_returns_drift_report_type(tmp_path):
    env_file = tmp_path / ".env"
    _write_env(env_file, "X=1\n")
    diff = DiffResult(missing_in_target=[], missing_in_base=[], mismatched={})
    bl = _make_baseline(tmp_path, diff)

    report = detect_drift(env_file, bl)
    assert isinstance(report, DriftReport)
    assert report.env_path == str(env_file)
    assert report.baseline_path == str(bl)


# ---------------------------------------------------------------------------
# update_baseline
# ---------------------------------------------------------------------------

def test_update_baseline_creates_file(tmp_path):
    env_file = tmp_path / ".env"
    _write_env(env_file, "FOO=bar\n")
    bl = tmp_path / "baseline.json"

    update_baseline(env_file, bl)
    assert bl.exists()


def test_update_baseline_is_valid_json(tmp_path):
    env_file = tmp_path / ".env"
    _write_env(env_file, "FOO=bar\nBAZ=qux\n")
    bl = tmp_path / "baseline.json"

    update_baseline(env_file, bl)
    data = json.loads(bl.read_text())
    assert isinstance(data, dict)
