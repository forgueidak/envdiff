"""Tests for envdiff.filter."""

import pytest

from envdiff.filter import filter_keys, filter_keys_many


SAMPLE: dict[str, str] = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_SECRET": "abc123",
    "APP_DEBUG": "true",
    "LOG_LEVEL": "info",
}


# ---------------------------------------------------------------------------
# filter_keys – include
# ---------------------------------------------------------------------------

def test_include_exact_match():
    result = filter_keys(SAMPLE, include=["DB_HOST"])
    assert result == {"DB_HOST": "localhost"}


def test_include_glob_prefix():
    result = filter_keys(SAMPLE, include=["DB_*"])
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_include_multiple_patterns():
    result = filter_keys(SAMPLE, include=["DB_*", "LOG_LEVEL"])
    assert set(result.keys()) == {"DB_HOST", "DB_PORT", "LOG_LEVEL"}


def test_include_no_match_returns_empty():
    result = filter_keys(SAMPLE, include=["REDIS_*"])
    assert result == {}


# ---------------------------------------------------------------------------
# filter_keys – exclude
# ---------------------------------------------------------------------------

def test_exclude_exact_match():
    result = filter_keys(SAMPLE, exclude=["LOG_LEVEL"])
    assert "LOG_LEVEL" not in result
    assert len(result) == len(SAMPLE) - 1


def test_exclude_glob():
    result = filter_keys(SAMPLE, exclude=["APP_*"])
    assert "APP_SECRET" not in result
    assert "APP_DEBUG" not in result
    assert "DB_HOST" in result


def test_exclude_all():
    result = filter_keys(SAMPLE, exclude=["*"])
    assert result == {}


# ---------------------------------------------------------------------------
# filter_keys – combined include + exclude
# ---------------------------------------------------------------------------

def test_include_then_exclude():
    # include all APP_ keys, then drop secrets
    result = filter_keys(SAMPLE, include=["APP_*"], exclude=["*SECRET*"])
    assert result == {"APP_DEBUG": "true"}


# ---------------------------------------------------------------------------
# filter_keys – no filters
# ---------------------------------------------------------------------------

def test_no_filters_returns_copy():
    result = filter_keys(SAMPLE)
    assert result == SAMPLE
    assert result is not SAMPLE


# ---------------------------------------------------------------------------
# filter_keys_many
# ---------------------------------------------------------------------------

def test_filter_keys_many_applies_to_all():
    envs = [
        {"DB_HOST": "localhost", "SECRET": "x"},
        {"DB_HOST": "prod-host", "SECRET": "y"},
    ]
    results = filter_keys_many(envs, include=["DB_*"])
    assert len(results) == 2
    assert all("SECRET" not in r for r in results)
    assert all("DB_HOST" in r for r in results)


def test_filter_keys_many_empty_list():
    assert filter_keys_many([], include=["DB_*"]) == []
