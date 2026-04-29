"""Tests for the envdiff CLI entry point."""

import json
from pathlib import Path

import pytest

from envdiff.cli import main


@pytest.fixture()
def tmp_env(tmp_path: Path):
    """Return a factory that writes a .env file and returns its path."""

    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)

    return _write


def test_no_differences_exit_zero(tmp_env):
    base = tmp_env(".env.base", "KEY=value\nOTHER=123\n")
    target = tmp_env(".env.target", "KEY=value\nOTHER=123\n")
    assert main([base, target, "--exit-code"]) == 0


def test_differences_exit_one_with_flag(tmp_env):
    base = tmp_env(".env.base", "KEY=value\nMISSING=x\n")
    target = tmp_env(".env.target", "KEY=value\n")
    assert main([base, target, "--exit-code"]) == 1


def test_differences_exit_zero_without_flag(tmp_env):
    base = tmp_env(".env.base", "KEY=value\nMISSING=x\n")
    target = tmp_env(".env.target", "KEY=value\n")
    assert main([base, target]) == 0


def test_missing_file_returns_2(tmp_env, tmp_path):
    base = tmp_env(".env.base", "KEY=value\n")
    missing = str(tmp_path / "nonexistent.env")
    assert main([base, missing]) == 2


def test_text_output_contains_key(tmp_env, capsys):
    base = tmp_env(".env.base", "SECRET_KEY=abc\nFOO=bar\n")
    target = tmp_env(".env.target", "FOO=bar\n")
    main([base, target])
    captured = capsys.readouterr()
    assert "SECRET_KEY" in captured.out


def test_json_output_is_valid(tmp_env, capsys):
    base = tmp_env(".env.base", "A=1\nB=2\n")
    target = tmp_env(".env.target", "A=1\n")
    main([base, target, "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "missing_in_target" in data


def test_markdown_output_contains_header(tmp_env, capsys):
    base = tmp_env(".env.base", "A=1\n")
    target = tmp_env(".env.target", "A=2\n")
    main([base, target, "--format", "markdown"])
    captured = capsys.readouterr()
    assert "#" in captured.out


def test_mask_secrets_flag(tmp_env, capsys):
    base = tmp_env(".env.base", "SECRET_TOKEN=supersecret\nFOO=bar\n")
    target = tmp_env(".env.target", "SECRET_TOKEN=different\nFOO=bar\n")
    main([base, target, "--mask-secrets"])
    captured = capsys.readouterr()
    assert "supersecret" not in captured.out
    assert "different" not in captured.out
