"""Tests for envdiff.duplicates."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.duplicates import (
    DuplicateReport,
    any_duplicates,
    find_duplicates,
    find_duplicates_many,
)


@pytest.fixture()
def tmp_env(tmp_path: Path):
    """Return a helper that writes a .env file under *tmp_path*."""

    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return p

    return _write


def test_no_duplicates_returns_empty_report(tmp_env):
    p = tmp_env("a.env", "FOO=1\nBAR=2\nBAZ=3\n")
    report = find_duplicates(p)
    assert not report.has_duplicates
    assert report.total_duplicate_keys == 0
    assert report.duplicates == {}


def test_single_duplicate_detected(tmp_env):
    p = tmp_env("b.env", "FOO=1\nFOO=2\nBAR=3\n")
    report = find_duplicates(p)
    assert report.has_duplicates
    assert "FOO" in report.duplicates
    assert report.duplicates["FOO"] == 2


def test_multiple_duplicates_detected(tmp_env):
    p = tmp_env("c.env", "A=1\nA=2\nA=3\nB=x\nB=y\n")
    report = find_duplicates(p)
    assert report.total_duplicate_keys == 2
    assert report.duplicates["A"] == 3
    assert report.duplicates["B"] == 2


def test_comments_and_blank_lines_ignored(tmp_env):
    p = tmp_env("d.env", "# comment\n\nFOO=1\n# another\nFOO=2\n")
    report = find_duplicates(p)
    assert report.duplicates["FOO"] == 2


def test_lines_without_equals_ignored(tmp_env):
    p = tmp_env("e.env", "NOEQUALS\nFOO=1\nFOO=2\n")
    report = find_duplicates(p)
    assert report.has_duplicates
    assert "NOEQUALS" not in report.duplicates


def test_summary_clean(tmp_env):
    p = tmp_env("f.env", "FOO=1\n")
    report = find_duplicates(p)
    assert "no duplicate" in report.summary()


def test_summary_with_duplicates(tmp_env):
    p = tmp_env("g.env", "KEY=a\nKEY=b\n")
    report = find_duplicates(p)
    summary = report.summary()
    assert "KEY" in summary
    assert "2 times" in summary


def test_find_duplicates_many(tmp_env):
    p1 = tmp_env("h1.env", "X=1\nX=2\n")
    p2 = tmp_env("h2.env", "Y=a\n")
    reports = find_duplicates_many([p1, p2])
    assert len(reports) == 2
    assert reports[0].has_duplicates
    assert not reports[1].has_duplicates


def test_any_duplicates_true(tmp_env):
    p = tmp_env("i.env", "Z=1\nZ=2\n")
    reports = find_duplicates_many([p])
    assert any_duplicates(reports)


def test_any_duplicates_false(tmp_env):
    p = tmp_env("j.env", "UNIQUE=1\n")
    reports = find_duplicates_many([p])
    assert not any_duplicates(reports)


def test_accepts_string_path(tmp_env):
    p = tmp_env("k.env", "FOO=1\nFOO=2\n")
    report = find_duplicates(str(p))
    assert report.has_duplicates
