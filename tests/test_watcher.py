"""Tests for envdiff.watcher."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envdiff.watcher import EnvWatcher


@pytest.fixture()
def env_pair(tmp_path):
    base = tmp_path / ".env.base"
    target = tmp_path / ".env.target"
    base.write_text("FOO=bar\nBAZ=qux\n")
    target.write_text("FOO=bar\n")
    return base, target


def test_snapshot_returns_diff(env_pair):
    base, target = env_pair
    watcher = EnvWatcher(base, target, callback=lambda r: None)
    result = watcher.snapshot()
    assert "BAZ" in result.missing_in_target


def test_snapshot_no_diff_when_equal(tmp_path):
    content = "FOO=bar\n"
    base = tmp_path / "a.env"
    target = tmp_path / "b.env"
    base.write_text(content)
    target.write_text(content)
    watcher = EnvWatcher(base, target, callback=lambda r: None)
    result = watcher.snapshot()
    assert not result.missing_in_target
    assert not result.missing_in_base
    assert not result.mismatched


def test_callback_invoked_on_change(env_pair):
    base, target = env_pair
    received: list = []
    watcher = EnvWatcher(base, target, callback=received.append, interval=0)
    # Force first iteration to detect change (mtimes differ from 0)
    watcher.start(max_iterations=1)
    assert len(received) == 1
    assert "BAZ" in received[0].missing_in_target


def test_callback_not_invoked_when_no_change(env_pair):
    base, target = env_pair
    received: list = []
    watcher = EnvWatcher(base, target, callback=received.append, interval=0)
    # Prime internal mtime cache so first poll sees no change
    watcher._last_mtimes = watcher._current_mtimes()
    watcher.start(max_iterations=1)
    assert len(received) == 0


def test_stop_ends_loop(env_pair):
    base, target = env_pair
    watcher = EnvWatcher(base, target, callback=lambda r: None, interval=0)
    watcher.stop()
    # After stop(), start with no max should exit immediately
    watcher.start(max_iterations=0)
    assert not watcher._running


def test_detects_file_modification(tmp_path):
    base = tmp_path / "base.env"
    target = tmp_path / "target.env"
    base.write_text("KEY=1\n")
    target.write_text("KEY=1\n")

    results: list = []
    watcher = EnvWatcher(base, target, callback=results.append, interval=0)
    watcher.start(max_iterations=1)  # primes mtime cache, no diff

    # Modify target
    time.sleep(0.01)
    target.write_text("KEY=2\n")
    watcher.start(max_iterations=1)

    assert len(results) >= 1
    last = results[-1]
    assert "KEY" in last.mismatched
