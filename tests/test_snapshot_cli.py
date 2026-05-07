"""Tests for envdiff.snapshot_cli."""
import argparse
import json
from pathlib import Path

import pytest

from envdiff.snapshot import capture, save_snapshot
from envdiff.snapshot_cli import build_snapshot_parser, run_snapshot_command


# ---------------------------------------------------------------- helpers ---

def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    build_snapshot_parser(sub)
    return parser


@pytest.fixture()
def env_pair(tmp_path):
    a = tmp_path / "base.env"
    b = tmp_path / "target.env"
    a.write_text("FOO=1\nBAR=2\n")
    b.write_text("FOO=1\nBAZ=3\n")
    return str(a), str(b)


# --------------------------------------------------------------- save -------

def test_save_creates_output_file(tmp_path, env_pair):
    env_a, _ = env_pair
    out = str(tmp_path / "snap.json")
    parser = _make_parser()
    args = parser.parse_args(["snapshot", "save", env_a, out])
    rc = run_snapshot_command(args)
    assert rc == 0
    assert Path(out).exists()


def test_save_output_is_valid_json(tmp_path, env_pair):
    env_a, _ = env_pair
    out = str(tmp_path / "snap.json")
    parser = _make_parser()
    args = parser.parse_args(["snapshot", "save", env_a, out])
    run_snapshot_command(args)
    data = json.loads(Path(out).read_text())
    assert "keys" in data
    assert "checksum" in data


def test_save_with_label(tmp_path, env_pair):
    env_a, _ = env_pair
    out = str(tmp_path / "snap.json")
    parser = _make_parser()
    args = parser.parse_args(["snapshot", "save", env_a, out, "--label", "prod"])
    run_snapshot_command(args)
    data = json.loads(Path(out).read_text())
    assert data["label"] == "prod"


# --------------------------------------------------------------- diff -------

def test_diff_identical_snapshots_exit_zero(tmp_path, env_pair):
    env_a, _ = env_pair
    snap_a = str(tmp_path / "a.json")
    snap_b = str(tmp_path / "b.json")
    s = capture(env_a)
    save_snapshot(s, snap_a)
    save_snapshot(s, snap_b)
    parser = _make_parser()
    args = parser.parse_args(["snapshot", "diff", snap_a, snap_b])
    assert run_snapshot_command(args) == 0


def test_diff_different_snapshots_exit_one(tmp_path, env_pair):
    env_a, env_b = env_pair
    snap_a = str(tmp_path / "a.json")
    snap_b = str(tmp_path / "b.json")
    save_snapshot(capture(env_a), snap_a)
    save_snapshot(capture(env_b), snap_b)
    parser = _make_parser()
    args = parser.parse_args(["snapshot", "diff", snap_a, snap_b])
    assert run_snapshot_command(args) == 1


def test_diff_json_format(tmp_path, env_pair, capsys):
    env_a, env_b = env_pair
    snap_a = str(tmp_path / "a.json")
    snap_b = str(tmp_path / "b.json")
    save_snapshot(capture(env_a), snap_a)
    save_snapshot(capture(env_b), snap_b)
    parser = _make_parser()
    args = parser.parse_args(["snapshot", "diff", snap_a, snap_b, "--format", "json"])
    run_snapshot_command(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "missing_in_target" in data or "mismatched" in data or "missing_in_base" in data
