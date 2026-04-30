"""Integration tests for the baseline CLI sub-commands."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.baseline import save_baseline
from envdiff.comparator import DiffResult
from envdiff.baseline_cli import run_baseline_command


class _Namespace:
    """Minimal stand-in for argparse.Namespace."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture()
def env_pair(tmp_path: Path):
    base = tmp_path / "base.env"
    target = tmp_path / "target.env"
    base.write_text("FOO=bar\nDB=local\nSECRET=abc\n")
    target.write_text("FOO=bar\nDB=prod\n")
    return base, target


def test_save_creates_baseline(env_pair, tmp_path):
    base, target = env_pair
    out = tmp_path / "bl.json"
    args = _Namespace(
        baseline_cmd="save",
        base=str(base),
        target=str(target),
        output=str(out),
    )
    rc = run_baseline_command(args)
    assert rc == 0
    assert out.exists()


def test_save_baseline_is_valid_json(env_pair, tmp_path):
    base, target = env_pair
    out = tmp_path / "bl.json"
    args = _Namespace(
        baseline_cmd="save",
        base=str(base),
        target=str(target),
        output=str(out),
    )
    run_baseline_command(args)
    data = json.loads(out.read_text())
    assert "version" in data


def test_compare_no_new_issues_returns_zero(env_pair, tmp_path):
    base, target = env_pair
    bl = tmp_path / "bl.json"
    # Save current state as baseline
    args_save = _Namespace(
        baseline_cmd="save", base=str(base), target=str(target), output=str(bl)
    )
    run_baseline_command(args_save)

    args_cmp = _Namespace(
        baseline_cmd="compare",
        base=str(base), target=str(target),
        baseline=str(bl), fmt="text", fail_on_new=True,
    )
    rc = run_baseline_command(args_cmp)
    assert rc == 0


def test_compare_new_issue_fails_with_flag(env_pair, tmp_path):
    base, target = env_pair
    bl = tmp_path / "bl.json"
    # Save empty baseline so everything looks new
    save_baseline(
        DiffResult(missing_in_target=set(), missing_in_base=set(), mismatched={}),
        bl,
    )
    args_cmp = _Namespace(
        baseline_cmd="compare",
        base=str(base), target=str(target),
        baseline=str(bl), fmt="text", fail_on_new=True,
    )
    rc = run_baseline_command(args_cmp)
    assert rc == 1


def test_compare_missing_baseline_returns_two(env_pair, tmp_path):
    base, target = env_pair
    args_cmp = _Namespace(
        baseline_cmd="compare",
        base=str(base), target=str(target),
        baseline=str(tmp_path / "nonexistent.json"),
        fmt="text", fail_on_new=False,
    )
    rc = run_baseline_command(args_cmp)
    assert rc == 2
