"""Tests for envdiff.normalizer."""

from __future__ import annotations

import pytest

from envdiff.normalizer import (
    NormalizedEnv,
    find_normalized_mismatches,
    normalize_many,
    normalize_value,
    values_equivalent,
)


# ---------------------------------------------------------------------------
# normalize_value
# ---------------------------------------------------------------------------


class TestNormalizeValue:
    def test_strips_whitespace(self):
        assert normalize_value("  hello  ") == "hello"

    def test_true_variants_become_true(self):
        for v in ("true", "True", "TRUE", "1", "yes", "YES", "on", "ON"):
            assert normalize_value(v) == "true", f"Expected 'true' for {v!r}"

    def test_false_variants_become_false(self):
        for v in ("false", "False", "FALSE", "0", "no", "NO", "off", "OFF"):
            assert normalize_value(v) == "false", f"Expected 'false' for {v!r}"

    def test_leading_zeros_stripped_from_integer(self):
        assert normalize_value("007") == "7"

    def test_negative_integer_preserved(self):
        assert normalize_value("-42") == "-42"

    def test_float_string_unchanged(self):
        assert normalize_value("3.14") == "3.14"

    def test_plain_string_unchanged(self):
        assert normalize_value("postgres") == "postgres"

    def test_empty_string_unchanged(self):
        assert normalize_value("") == ""


# ---------------------------------------------------------------------------
# values_equivalent
# ---------------------------------------------------------------------------


def test_equivalent_booleans():
    assert values_equivalent("yes", "true") is True


def test_equivalent_integers_with_leading_zeros():
    assert values_equivalent("007", "7") is True


def test_non_equivalent_values():
    assert values_equivalent("foo", "bar") is False


# ---------------------------------------------------------------------------
# NormalizedEnv
# ---------------------------------------------------------------------------


def test_normalized_env_populates_normalized():
    raw = {"DEBUG": "yes", "PORT": "08080", "NAME": "app"}
    env = NormalizedEnv(original=raw)
    assert env.normalized["DEBUG"] == "true"
    assert env.normalized["PORT"] == "8080"
    assert env.normalized["NAME"] == "app"


def test_normalized_env_original_unchanged():
    raw = {"DEBUG": "yes"}
    env = NormalizedEnv(original=raw)
    assert env.original["DEBUG"] == "yes"


# ---------------------------------------------------------------------------
# normalize_many
# ---------------------------------------------------------------------------


def test_normalize_many_returns_all_labels():
    envs = {"dev": {"A": "1"}, "prod": {"A": "true"}}
    result = normalize_many(envs)
    assert set(result.keys()) == {"dev", "prod"}
    assert isinstance(result["dev"], NormalizedEnv)


# ---------------------------------------------------------------------------
# find_normalized_mismatches
# ---------------------------------------------------------------------------


def test_no_mismatches_for_equivalent_values():
    base = {"DEBUG": "yes", "PORT": "8080"}
    target = {"DEBUG": "true", "PORT": "8080"}
    assert find_normalized_mismatches(base, target) == {}


def test_mismatch_reported_for_different_values():
    base = {"HOST": "localhost", "PORT": "5432"}
    target = {"HOST": "remotehost", "PORT": "5432"}
    result = find_normalized_mismatches(base, target)
    assert "HOST" in result
    assert result["HOST"] == {"base": "localhost", "target": "remotehost"}


def test_keys_missing_in_either_side_not_in_mismatches():
    base = {"ONLY_BASE": "x", "SHARED": "same"}
    target = {"ONLY_TARGET": "y", "SHARED": "same"}
    result = find_normalized_mismatches(base, target)
    assert result == {}


def test_mask_secrets_hides_values():
    base = {"SECRET_KEY": "abc123"}
    target = {"SECRET_KEY": "xyz789"}
    result = find_normalized_mismatches(base, target, mask_secrets=True)
    assert result["SECRET_KEY"] == {"base": "***", "target": "***"}


def test_mask_secrets_false_shows_values():
    base = {"SECRET_KEY": "abc123"}
    target = {"SECRET_KEY": "xyz789"}
    result = find_normalized_mismatches(base, target, mask_secrets=False)
    assert result["SECRET_KEY"] == {"base": "abc123", "target": "xyz789"}
