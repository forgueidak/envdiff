"""Tests for envdiff.changelog_cli."""
import argparse
import json
from pathlib import Path

import pytest

from envdiff.changelog_cli import build_changelog_parser, run_changelog_command


@pytest.fixture
def env_pair(tmp_path):
    base = tmp_path / ".env.base"
    target = tmp_path / ".env.target"
    base.write_text("DB_HOST=localhost\nAPI_KEY=secret\nSHARED=same\n")
    target.write_text("API_KEY=secret\nSHARED=same\nNEW_KEY=added\n")
    return base, target


def _make_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    build_changelog_parser(sub)
    return parser


def test_record_creates_changelog_file(env_pair, tmp_path):
    base, target = env_pair
    cl_path = tmp_path / "cl.json"
    parser = _make_parser()
    args = parser.parse_args(
        ["changelog", "record", str(base), str(target), "--changelog", str(cl_path)]
    )
    rc = run_changelog_command(args)
    assert rc == 0
    assert cl_path.exists()


def test_record_output_is_valid_json(env_pair, tmp_path):
    base, target = env_pair
    cl_path = tmp_path / "cl.json"
    parser = _make_parser()
    args = parser.parse_args(
        ["changelog", "record", str(base), str(target), "--changelog", str(cl_path)]
    )
    run_changelog_command(args)
    data = json.loads(cl_path.read_text())
    assert "entries" in data


def test_record_appends_on_second_call(env_pair, tmp_path):
    base, target = env_pair
    cl_path = tmp_path / "cl.json"
    parser = _make_parser()
    for _ in range(2):
        args = parser.parse_args(
            ["changelog", "record", str(base), str(target), "--changelog", str(cl_path)]
        )
        run_changelog_command(args)
    data = json.loads(cl_path.read_text())
    assert len(data["entries"]) == 2


def test_show_returns_one_when_no_file(tmp_path):
    cl_path = tmp_path / "nonexistent.json"
    parser = _make_parser()
    args = parser.parse_args(
        ["changelog", "show", "--changelog", str(cl_path)]
    )
    rc = run_changelog_command(args)
    assert rc == 1


def test_show_prints_entries(env_pair, tmp_path, capsys):
    base, target = env_pair
    cl_path = tmp_path / "cl.json"
    parser = _make_parser()
    rec_args = parser.parse_args(
        ["changelog", "record", str(base), str(target), "--changelog", str(cl_path)]
    )
    run_changelog_command(rec_args)
    show_args = parser.parse_args(
        ["changelog", "show", "--changelog", str(cl_path)]
    )
    rc = run_changelog_command(show_args)
    assert rc == 0
    captured = capsys.readouterr()
    assert "issues=" in captured.out


def test_show_limit_restricts_output(env_pair, tmp_path, capsys):
    base, target = env_pair
    cl_path = tmp_path / "cl.json"
    parser = _make_parser()
    for _ in range(3):
        args = parser.parse_args(
            ["changelog", "record", str(base), str(target), "--changelog", str(cl_path)]
        )
        run_changelog_command(args)
    show_args = parser.parse_args(
        ["changelog", "show", "--changelog", str(cl_path), "--limit", "1"]
    )
    run_changelog_command(show_args)
    captured = capsys.readouterr()
    assert captured.out.count("issues=") == 1
