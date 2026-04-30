"""Tests for envdiff.differ — high-level diff runner."""

from pathlib import Path

import pytest

from envdiff.differ import DiffOptions, run_diff


@pytest.fixture()
def env_pair(tmp_path: Path):
    base = tmp_path / ".env.base"
    target = tmp_path / ".env.target"

    base.write_text(
        "APP_NAME=myapp\n"
        "SECRET_KEY=supersecret\n"
        "DEBUG=true\n"
        "ONLY_IN_BASE=yes\n"
    )
    target.write_text(
        "APP_NAME=myapp\n"
        "SECRET_KEY=different\n"
        "DEBUG=false\n"
        "ONLY_IN_TARGET=yes\n"
    )
    return base, target


def test_run_diff_returns_diff_run(env_pair):
    base, target = env_pair
    run = run_diff(base, target)
    assert run.base_path == base
    assert run.target_path == target


def test_run_diff_detects_missing_in_target(env_pair):
    base, target = env_pair
    run = run_diff(base, target)
    assert "ONLY_IN_BASE" in run.result.missing_in_target


def test_run_diff_detects_missing_in_base(env_pair):
    base, target = env_pair
    run = run_diff(base, target)
    assert "ONLY_IN_TARGET" in run.result.missing_in_base


def test_run_diff_detects_mismatch(env_pair):
    base, target = env_pair
    run = run_diff(base, target)
    keys = [k for k, *_ in run.result.mismatched]
    assert "DEBUG" in keys


def test_run_diff_summary_has_issues(env_pair):
    base, target = env_pair
    run = run_diff(base, target)
    assert run.summary.has_issues()


def test_run_diff_include_filter(env_pair):
    base, target = env_pair
    opts = DiffOptions(include_patterns=["APP_*"])
    run = run_diff(base, target, options=opts)
    # Only APP_NAME survives; it matches in both — no differences expected
    assert not run.result.missing_in_target
    assert not run.result.missing_in_base
    assert not run.result.mismatched


def test_run_diff_exclude_filter(env_pair):
    base, target = env_pair
    opts = DiffOptions(exclude_patterns=["ONLY_*"])
    run = run_diff(base, target, options=opts)
    assert "ONLY_IN_BASE" not in run.result.missing_in_target
    assert "ONLY_IN_TARGET" not in run.result.missing_in_base


def test_run_diff_default_options_masks_secrets(env_pair):
    base, target = env_pair
    run = run_diff(base, target)
    secret_row = next(
        (row for row in run.result.mismatched if row[0] == "SECRET_KEY"), None
    )
    # With masking the values should not be the raw secrets
    if secret_row:
        assert secret_row[1] != "supersecret"
        assert secret_row[2] != "different"


def test_run_diff_no_mask(env_pair):
    base, target = env_pair
    opts = DiffOptions(mask_secrets=False)
    run = run_diff(base, target, options=opts)
    secret_row = next(
        (row for row in run.result.mismatched if row[0] == "SECRET_KEY"), None
    )
    assert secret_row is not None
    assert secret_row[1] == "supersecret"
    assert secret_row[2] == "different"
