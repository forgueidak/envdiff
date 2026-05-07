"""Tests for envdiff.profiler."""
from __future__ import annotations

import os
import tempfile

import pytest

from envdiff.profiler import EnvProfile, profile_env, profile_many


def _write(content: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".env")
    with os.fdopen(fd, "w") as fh:
        fh.write(content)
    return path


@pytest.fixture()
def simple_env(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "APP_NAME=myapp\n"
        "SECRET_KEY=supersecret\n"
        "DB_PASSWORD=hunter2\n"
        "DEBUG=true\n"
        "EMPTY_VAL=\n"
    )
    return str(p)


def test_profile_returns_env_profile(simple_env):
    result = profile_env(simple_env)
    assert isinstance(result, EnvProfile)


def test_profile_total_keys(simple_env):
    result = profile_env(simple_env)
    assert result.total_keys == 5


def test_profile_secret_keys_detected(simple_env):
    result = profile_env(simple_env)
    assert "SECRET_KEY" in result.secret_keys
    assert "DB_PASSWORD" in result.secret_keys


def test_profile_plain_keys_detected(simple_env):
    result = profile_env(simple_env)
    assert "APP_NAME" in result.plain_keys
    assert "DEBUG" in result.plain_keys


def test_profile_empty_keys_detected(simple_env):
    result = profile_env(simple_env)
    assert "EMPTY_VAL" in result.empty_keys


def test_profile_secret_ratio(simple_env):
    result = profile_env(simple_env)
    # 2 secrets out of 5 total
    assert result.secret_ratio == pytest.approx(0.4, abs=1e-4)


def test_profile_no_duplicates(simple_env):
    result = profile_env(simple_env)
    assert result.duplicate_keys == []


def test_profile_empty_file():
    path = _write("")
    result = profile_env(path)
    assert result.total_keys == 0
    assert result.secret_ratio == 0.0


def test_as_dict_contains_expected_keys(simple_env):
    d = profile_env(simple_env).as_dict()
    for key in ("path", "total_keys", "secret_count", "plain_count",
                "empty_count", "duplicate_count", "secret_ratio",
                "secret_keys", "plain_keys", "empty_keys", "duplicate_keys"):
        assert key in d, f"missing key: {key}"


def test_profile_many_returns_one_per_path(tmp_path):
    p1 = tmp_path / "a.env"
    p2 = tmp_path / "b.env"
    p1.write_text("FOO=1\n")
    p2.write_text("BAR=2\nSECRET_KEY=x\n")
    results = profile_many([str(p1), str(p2)])
    assert len(results) == 2
    assert results[0].path == str(p1)
    assert results[1].secret_count == 1
