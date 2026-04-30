"""Tests for envdiff.annotator."""

import pytest

from envdiff.annotator import AnnotatedLine, annotate
from envdiff.comparator import DiffResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _result(
    missing_in_target=None,
    missing_in_base=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        missing_in_target=missing_in_target or [],
        missing_in_base=missing_in_base or [],
        mismatched=mismatched or [],
    )


# ---------------------------------------------------------------------------
# Basic status assignment
# ---------------------------------------------------------------------------

def test_ok_key_gets_ok_status():
    base = {"HOST": "localhost"}
    target = {"HOST": "localhost"}
    result = _result()
    diff = annotate(base, target, result)
    assert diff.lines[0].status == "ok"


def test_missing_in_target_status():
    base = {"SECRET": "abc"}
    target = {}
    result = _result(missing_in_target=["SECRET"])
    diff = annotate(base, target, result)
    line = diff.lines[0]
    assert line.status == "missing_in_target"
    assert line.base_value == "abc"
    assert line.target_value is None


def test_missing_in_base_status():
    base = {}
    target = {"NEW_KEY": "val"}
    result = _result(missing_in_base=["NEW_KEY"])
    diff = annotate(base, target, result)
    line = diff.lines[0]
    assert line.status == "missing_in_base"
    assert line.base_value is None
    assert line.target_value == "val"


def test_mismatched_status():
    base = {"PORT": "8080"}
    target = {"PORT": "9090"}
    result = _result(mismatched=[("PORT", "8080", "9090")])
    diff = annotate(base, target, result)
    line = diff.lines[0]
    assert line.status == "mismatched"
    assert line.base_value == "8080"
    assert line.target_value == "9090"


# ---------------------------------------------------------------------------
# AnnotatedDiff helpers
# ---------------------------------------------------------------------------

def test_has_issues_false_when_all_ok():
    base = {"A": "1", "B": "2"}
    target = {"A": "1", "B": "2"}
    diff = annotate(base, target, _result())
    assert not diff.has_issues


def test_has_issues_true_when_mismatch():
    base = {"A": "1"}
    target = {"A": "2"}
    result = _result(mismatched=[("A", "1", "2")])
    diff = annotate(base, target, result)
    assert diff.has_issues


def test_by_status_filters_correctly():
    base = {"X": "1", "Y": "old"}
    target = {"Y": "new"}
    result = _result(missing_in_target=["X"], mismatched=[("Y", "old", "new")])
    diff = annotate(base, target, result)
    assert len(diff.by_status("missing_in_target")) == 1
    assert len(diff.by_status("mismatched")) == 1
    assert len(diff.by_status("ok")) == 0


def test_keys_are_sorted():
    base = {"ZEBRA": "z", "ALPHA": "a", "MANGO": "m"}
    target = {"ZEBRA": "z", "ALPHA": "a", "MANGO": "m"}
    diff = annotate(base, target, _result())
    keys = [ln.key for ln in diff.lines]
    assert keys == sorted(keys)


def test_paths_stored_on_annotated_diff():
    diff = annotate({}, {}, _result(), base_path=".env.dev", target_path=".env.prod")
    assert diff.base_path == ".env.dev"
    assert diff.target_path == ".env.prod"


def test_is_ok_property():
    line_ok = AnnotatedLine(key="K", value="v", status="ok")
    line_bad = AnnotatedLine(key="K", value=None, status="missing_in_target")
    assert line_ok.is_ok
    assert not line_bad.is_ok
