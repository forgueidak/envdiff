"""Tests for envdiff.linter."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from envdiff.linter import LintIssue, LintResult, lint_env_file, lint_many


@pytest.fixture()
def tmp_env(tmp_path: Path):
    """Factory that writes a temp .env file and returns its path string."""

    def _write(content: str) -> str:
        p = tmp_path / "test.env"
        p.write_text(textwrap.dedent(content), encoding="utf-8")
        return str(p)

    return _write


def test_clean_file_has_no_issues(tmp_env):
    path = tmp_env("""\
        DATABASE_URL=postgres://localhost/db
        SECRET_KEY=supersecret
        PORT=5432
    """)
    result = lint_env_file(path)
    assert result.is_clean
    assert result.issue_count == 0


def test_lowercase_key_triggers_w001(tmp_env):
    path = tmp_env("database_url=postgres://localhost/db\n")
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "W001" in codes


def test_empty_value_triggers_w002(tmp_env):
    path = tmp_env("MY_KEY=\n")
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "W002" in codes


def test_missing_equals_triggers_e001(tmp_env):
    path = tmp_env("NOTAVALIDLINE\n")
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "E001" in codes


def test_key_with_space_triggers_e003(tmp_env):
    path = tmp_env("MY KEY=value\n")
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "E003" in codes


def test_unmatched_double_quote_triggers_e004(tmp_env):
    path = tmp_env('MY_KEY="unclosed\n')
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "E004" in codes


def test_unmatched_single_quote_triggers_e004(tmp_env):
    path = tmp_env("MY_KEY='unclosed\n")
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "E004" in codes


def test_comments_and_blank_lines_ignored(tmp_env):
    path = tmp_env("""\
        # This is a comment

        VALID_KEY=value
    """)
    result = lint_env_file(path)
    assert result.is_clean


def test_by_code_filters_correctly(tmp_env):
    path = tmp_env("lowercase=value\nANOTHER_LOWER=\n")
    result = lint_env_file(path)
    w001 = result.by_code("W001")
    assert all(i.code == "W001" for i in w001)


def test_lint_many_returns_one_result_per_file(tmp_path):
    files = []
    for name in ("a.env", "b.env"):
        p = tmp_path / name
        p.write_text("KEY=value\n", encoding="utf-8")
        files.append(str(p))

    results = lint_many(files)
    assert len(results) == 2
    assert all(isinstance(r, LintResult) for r in results)


def test_lint_issue_str_format(tmp_env):
    path = tmp_env("bad line\n")
    result = lint_env_file(path)
    issue = result.issues[0]
    text = str(issue)
    assert "E001" in text
    assert "Line 1" in text
