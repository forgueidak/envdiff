"""Tests for envdiff.validator."""

import pytest

from envdiff.validator import KeySchema, ValidationResult, validate_env, validate_many


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BASE_SCHEMA = {
    "DATABASE_URL": KeySchema(required=True, expected_type="url"),
    "PORT": KeySchema(required=True, expected_type="int"),
    "DEBUG": KeySchema(required=False, expected_type="bool"),
    "APP_NAME": KeySchema(required=True),
}


# ---------------------------------------------------------------------------
# missing_required
# ---------------------------------------------------------------------------


def test_missing_required_key_reported():
    env = {"DATABASE_URL": "https://db", "PORT": "5432"}
    result = validate_env(env, BASE_SCHEMA)
    assert "APP_NAME" in result.missing_required
    assert not result.is_valid


def test_all_required_present_no_missing():
    env = {"DATABASE_URL": "https://db", "PORT": "5432", "APP_NAME": "myapp"}
    result = validate_env(env, BASE_SCHEMA)
    assert result.missing_required == []


def test_optional_key_absence_not_reported():
    env = {"DATABASE_URL": "https://db", "PORT": "5432", "APP_NAME": "myapp"}
    result = validate_env(env, BASE_SCHEMA)
    # DEBUG is optional — should not appear in missing_required
    assert "DEBUG" not in result.missing_required


# ---------------------------------------------------------------------------
# type validation
# ---------------------------------------------------------------------------


def test_invalid_int_reported():
    env = {"DATABASE_URL": "https://db", "PORT": "not_a_number", "APP_NAME": "x"}
    result = validate_env(env, BASE_SCHEMA)
    assert "PORT" in result.type_errors


def test_valid_int_no_error():
    env = {"DATABASE_URL": "https://db", "PORT": "5432", "APP_NAME": "x"}
    result = validate_env(env, BASE_SCHEMA)
    assert "PORT" not in result.type_errors


def test_invalid_bool_reported():
    env = {
        "DATABASE_URL": "https://db",
        "PORT": "5432",
        "APP_NAME": "x",
        "DEBUG": "maybe",
    }
    result = validate_env(env, BASE_SCHEMA)
    assert "DEBUG" in result.type_errors


@pytest.mark.parametrize("val", ["true", "false", "1", "0", "yes", "no", "True", "YES"])
def test_valid_bool_values(val):
    env = {"DATABASE_URL": "https://db", "PORT": "5432", "APP_NAME": "x", "DEBUG": val}
    result = validate_env(env, BASE_SCHEMA)
    assert "DEBUG" not in result.type_errors


def test_invalid_url_reported():
    env = {"DATABASE_URL": "postgres://db", "PORT": "5432", "APP_NAME": "x"}
    result = validate_env(env, BASE_SCHEMA)
    assert "DATABASE_URL" in result.type_errors


def test_valid_url_no_error():
    env = {"DATABASE_URL": "https://db", "PORT": "5432", "APP_NAME": "x"}
    result = validate_env(env, BASE_SCHEMA)
    assert "DATABASE_URL" not in result.type_errors


# ---------------------------------------------------------------------------
# unknown keys
# ---------------------------------------------------------------------------


def test_unknown_keys_reported_when_disallowed():
    env = {"DATABASE_URL": "https://db", "PORT": "5432", "APP_NAME": "x", "EXTRA": "y"}
    result = validate_env(env, BASE_SCHEMA, allow_unknown=False)
    assert "EXTRA" in result.unknown_keys


def test_unknown_keys_ignored_by_default():
    env = {"DATABASE_URL": "https://db", "PORT": "5432", "APP_NAME": "x", "EXTRA": "y"}
    result = validate_env(env, BASE_SCHEMA)
    assert result.unknown_keys == []


# ---------------------------------------------------------------------------
# validate_many
# ---------------------------------------------------------------------------


def test_validate_many_returns_per_env_results():
    envs = {
        "production": {"DATABASE_URL": "https://db", "PORT": "5432", "APP_NAME": "x"},
        "staging": {"DATABASE_URL": "https://db", "PORT": "bad", "APP_NAME": "x"},
    }
    results = validate_many(envs, BASE_SCHEMA)
    assert results["production"].is_valid
    assert not results["staging"].is_valid
    assert "PORT" in results["staging"].type_errors
