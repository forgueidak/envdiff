"""Tests for envdiff.template_cli."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from envdiff.template_cli import build_template_parser, run_template_command


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


class _Namespace(argparse.Namespace):
    """Minimal namespace that mirrors the CLI args."""

    def __init__(self, env_file: str, output: str | None = None,
                 preserve_values: bool = False, quiet: bool = False):
        super().__init__()
        self.env_file = env_file
        self.output = output
        self.preserve_values = preserve_values
        self.quiet = quiet


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    return _write(
        tmp_path / ".env",
        "APP_NAME=myapp\nSECRET_KEY=s3cr3t\nPORT=8080\nAPI_TOKEN=tok_xyz\n",
    )


# ---------------------------------------------------------------------------
# build_template_parser
# ---------------------------------------------------------------------------

def test_parser_returns_argument_parser():
    parser = build_template_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_parser_has_env_file_positional():
    parser = build_template_parser()
    # Should not raise when env_file is provided
    args = parser.parse_args(["some.env"])
    assert args.env_file == "some.env"


def test_parser_default_output_is_none():
    parser = build_template_parser()
    args = parser.parse_args(["some.env"])
    assert args.output is None


def test_parser_preserve_values_flag():
    parser = build_template_parser()
    args = parser.parse_args(["some.env", "--preserve-values"])
    assert args.preserve_values is True


# ---------------------------------------------------------------------------
# run_template_command
# ---------------------------------------------------------------------------

def test_missing_file_returns_exit_code_2(tmp_path: Path):
    ns = _Namespace(env_file=str(tmp_path / "nonexistent.env"))
    assert run_template_command(ns) == 2


def test_creates_default_template_file(env_file: Path):
    ns = _Namespace(env_file=str(env_file), quiet=True)
    rc = run_template_command(ns)
    assert rc == 0
    expected = Path(str(env_file) + ".template")
    assert expected.exists()


def test_custom_output_path(env_file: Path, tmp_path: Path):
    out = str(tmp_path / "custom.template")
    ns = _Namespace(env_file=str(env_file), output=out, quiet=True)
    rc = run_template_command(ns)
    assert rc == 0
    assert Path(out).exists()


def test_template_contains_all_keys(env_file: Path, tmp_path: Path):
    out = str(tmp_path / "out.template")
    ns = _Namespace(env_file=str(env_file), output=out, quiet=True)
    run_template_command(ns)
    content = Path(out).read_text()
    for key in ("APP_NAME", "SECRET_KEY", "PORT", "API_TOKEN"):
        assert key in content


def test_secret_values_are_replaced(env_file: Path, tmp_path: Path):
    out = str(tmp_path / "out.template")
    ns = _Namespace(env_file=str(env_file), output=out, quiet=True)
    run_template_command(ns)
    content = Path(out).read_text()
    assert "s3cr3t" not in content
    assert "tok_xyz" not in content


def test_preserve_values_keeps_non_secret(env_file: Path, tmp_path: Path):
    out = str(tmp_path / "out.template")
    ns = _Namespace(env_file=str(env_file), output=out,
                    preserve_values=True, quiet=True)
    run_template_command(ns)
    content = Path(out).read_text()
    assert "8080" in content  # PORT is non-secret
    assert "myapp" in content  # APP_NAME is non-secret


def test_exit_code_zero_on_success(env_file: Path):
    ns = _Namespace(env_file=str(env_file), quiet=True)
    assert run_template_command(ns) == 0


def test_quiet_flag_suppresses_output(env_file: Path, capsys):
    ns = _Namespace(env_file=str(env_file), quiet=True)
    run_template_command(ns)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_verbose_output_shows_key_counts(env_file: Path, capsys):
    ns = _Namespace(env_file=str(env_file), quiet=False)
    run_template_command(ns)
    captured = capsys.readouterr()
    assert "Total keys" in captured.out
    assert "Secret keys" in captured.out
