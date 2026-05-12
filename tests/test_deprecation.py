"""Tests for envdiff.deprecation."""
import pytest

from envdiff.deprecation import (
    DeprecationRule,
    DeprecationReport,
    DeprecationHit,
    check_deprecations,
)


# ---------------------------------------------------------------------------
# DeprecationRule.message
# ---------------------------------------------------------------------------

def test_rule_message_with_new_key_and_reason():
    rule = DeprecationRule(old_key="OLD_DB_URL", new_key="DATABASE_URL", reason="renamed in v2")
    msg = rule.message()
    assert "'OLD_DB_URL' is deprecated" in msg
    assert "'DATABASE_URL'" in msg
    assert "renamed in v2" in msg


def test_rule_message_without_replacement():
    rule = DeprecationRule(old_key="LEGACY_FLAG")
    assert rule.message() == "'LEGACY_FLAG' is deprecated"


def test_rule_message_with_reason_only():
    rule = DeprecationRule(old_key="OLD_KEY", reason="no longer used")
    msg = rule.message()
    assert "no longer used" in msg
    assert "use" not in msg


# ---------------------------------------------------------------------------
# DeprecationHit.__str__
# ---------------------------------------------------------------------------

def test_hit_str_contains_deprecated_label():
    rule = DeprecationRule(old_key="LEGACY", new_key="CURRENT")
    hit = DeprecationHit(key="LEGACY", rule=rule)
    assert str(hit).startswith("[DEPRECATED]")


# ---------------------------------------------------------------------------
# check_deprecations — happy paths
# ---------------------------------------------------------------------------

def test_no_deprecated_keys_returns_empty_report():
    env = {"DATABASE_URL": "postgres://", "SECRET_KEY": "abc"}
    rules = [DeprecationRule(old_key="OLD_DB_URL", new_key="DATABASE_URL")]
    report = check_deprecations(env, rules)
    assert not report.has_hits
    assert report.hit_count == 0
    assert report.scanned_keys == 2


def test_deprecated_key_detected():
    env = {"OLD_DB_URL": "postgres://", "SECRET_KEY": "abc"}
    rules = [DeprecationRule(old_key="OLD_DB_URL", new_key="DATABASE_URL")]
    report = check_deprecations(env, rules)
    assert report.has_hits
    assert report.hit_count == 1
    assert report.hits[0].key == "OLD_DB_URL"


def test_multiple_deprecated_keys_all_detected():
    env = {"OLD_DB_URL": "x", "LEGACY_FLAG": "true", "SAFE_KEY": "ok"}
    rules = [
        DeprecationRule(old_key="OLD_DB_URL"),
        DeprecationRule(old_key="LEGACY_FLAG"),
    ]
    report = check_deprecations(env, rules)
    assert report.hit_count == 2
    hit_keys = {h.key for h in report.hits}
    assert hit_keys == {"OLD_DB_URL", "LEGACY_FLAG"}


def test_scanned_keys_reflects_env_size():
    env = {"A": "1", "B": "2", "C": "3"}
    report = check_deprecations(env, [])
    assert report.scanned_keys == 3


# ---------------------------------------------------------------------------
# as_dict
# ---------------------------------------------------------------------------

def test_as_dict_structure():
    env = {"OLD_KEY": "val"}
    rules = [DeprecationRule(old_key="OLD_KEY", new_key="NEW_KEY", reason="test")]
    report = check_deprecations(env, rules)
    d = report.as_dict()
    assert d["scanned_keys"] == 1
    assert d["hit_count"] == 1
    assert d["hits"][0]["key"] == "OLD_KEY"
    assert d["hits"][0]["new_key"] == "NEW_KEY"
    assert d["hits"][0]["reason"] == "test"


def test_as_dict_empty_hits():
    report = DeprecationReport(scanned_keys=5)
    d = report.as_dict()
    assert d["hits"] == []
    assert d["hit_count"] == 0
