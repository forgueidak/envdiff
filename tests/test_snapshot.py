"""Tests for envdiff.snapshot."""
import json
from pathlib import Path

import pytest

from envdiff.snapshot import (
    EnvSnapshot,
    capture,
    load_snapshot,
    save_snapshot,
    snapshots_equal,
    _checksum,
)


@pytest.fixture()
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)

    return _write


# ------------------------------------------------------------------ capture --

def test_capture_returns_snapshot(tmp_env):
    path = tmp_env("a.env", "FOO=bar\nBAZ=qux\n")
    snap = capture(path)
    assert isinstance(snap, EnvSnapshot)
    assert snap.keys == {"FOO": "bar", "BAZ": "qux"}


def test_capture_sets_path(tmp_env):
    path = tmp_env("a.env", "X=1\n")
    snap = capture(path)
    assert snap.path == path


def test_capture_sets_label(tmp_env):
    path = tmp_env("a.env", "X=1\n")
    snap = capture(path, label="production")
    assert snap.label == "production"


def test_capture_label_defaults_none(tmp_env):
    path = tmp_env("a.env", "X=1\n")
    snap = capture(path)
    assert snap.label is None


def test_capture_checksum_is_hex_string(tmp_env):
    path = tmp_env("a.env", "X=1\n")
    snap = capture(path)
    assert len(snap.checksum) == 64
    assert all(c in "0123456789abcdef" for c in snap.checksum)


# ---------------------------------------------------------------- checksum --

def test_checksum_deterministic():
    data = {"A": "1", "B": "2"}
    assert _checksum(data) == _checksum(data)


def test_checksum_order_independent():
    assert _checksum({"A": "1", "B": "2"}) == _checksum({"B": "2", "A": "1"})


def test_checksum_differs_on_value_change():
    assert _checksum({"A": "1"}) != _checksum({"A": "2"})


# --------------------------------------------------------- save / load ------

def test_save_creates_file(tmp_env, tmp_path):
    path = tmp_env("a.env", "K=v\n")
    snap = capture(path, label="dev")
    dest = str(tmp_path / "snap.json")
    save_snapshot(snap, dest)
    assert Path(dest).exists()


def test_save_file_is_valid_json(tmp_env, tmp_path):
    path = tmp_env("a.env", "K=v\n")
    snap = capture(path)
    dest = str(tmp_path / "snap.json")
    save_snapshot(snap, dest)
    data = json.loads(Path(dest).read_text())
    assert "keys" in data and "checksum" in data


def test_roundtrip_preserves_keys(tmp_env, tmp_path):
    path = tmp_env("a.env", "FOO=bar\n")
    snap = capture(path)
    dest = str(tmp_path / "snap.json")
    save_snapshot(snap, dest)
    loaded = load_snapshot(dest)
    assert loaded.keys == snap.keys
    assert loaded.checksum == snap.checksum


# -------------------------------------------------------- snapshots_equal ---

def test_snapshots_equal_same_content(tmp_env):
    path = tmp_env("a.env", "X=1\n")
    s1 = capture(path)
    s2 = capture(path)
    assert snapshots_equal(s1, s2)


def test_snapshots_not_equal_different_content(tmp_env, tmp_path):
    p1 = tmp_env("a.env", "X=1\n")
    p2 = str(tmp_path / "b.env")
    Path(p2).write_text("X=2\n")
    s1 = capture(p1)
    s2 = capture(p2)
    assert not snapshots_equal(s1, s2)


# ------------------------------------------------------------ as_dict ------

def test_as_dict_contains_key_count(tmp_env):
    path = tmp_env("a.env", "A=1\nB=2\n")
    snap = capture(path)
    d = snap.as_dict()
    assert d["key_count"] == 2
