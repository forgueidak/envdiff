"""Tests for envdiff.comparator module."""

import pytest
from envdiff.comparator import compare_envs, DiffResult, _is_secret


BASE_ENV = {
    "APP_NAME": "myapp",
    "DEBUG": "true",
    "DB_PASSWORD": "secret123",
    "API_KEY": "abc",
    "PORT": "8080",
}

TARGET_ENV = {
    "APP_NAME": "myapp",
    "DEBUG": "false",
    "DB_PASSWORD": "prod_secret",
    "API_KEY": "abc",
    "LOG_LEVEL": "info",
}


def test_missing_in_target():
    result = compare_envs(BASE_ENV, TARGET_ENV)
    assert "PORT" in result.missing_in_target
    assert "APP_NAME" not in result.missing_in_target


def test_missing_in_base():
    result = compare_envs(BASE_ENV, TARGET_ENV)
    assert "LOG_LEVEL" in result.missing_in_base
    assert "DEBUG" not in result.missing_in_base


def test_mismatched_keys():
    result = compare_envs(BASE_ENV, TARGET_ENV)
    assert "DEBUG" in result.mismatched
    assert result.mismatched["DEBUG"]["base"] == "true"
    assert result.mismatched["DEBUG"]["target"] == "false"


def test_no_mismatch_for_equal_values():
    result = compare_envs(BASE_ENV, TARGET_ENV)
    assert "APP_NAME" not in result.mismatched
    assert "API_KEY" not in result.mismatched


def test_mask_secrets_hides_values():
    result = compare_envs(BASE_ENV, TARGET_ENV, mask_secrets=True)
    assert "DB_PASSWORD" in result.mismatched
    assert result.mismatched["DB_PASSWORD"]["base"] == "***"
    assert result.mismatched["DB_PASSWORD"]["target"] == "***"


def test_mask_secrets_does_not_hide_non_secrets():
    result = compare_envs(BASE_ENV, TARGET_ENV, mask_secrets=True)
    assert result.mismatched["DEBUG"]["base"] == "true"
    assert result.mismatched["DEBUG"]["target"] == "false"


def test_custom_secret_keywords():
    result = compare_envs(
        BASE_ENV, TARGET_ENV, mask_secrets=True, secret_keywords=["debug"]
    )
    assert result.mismatched["DEBUG"]["base"] == "***"
    assert result.mismatched["DB_PASSWORD"]["base"] != "***"


def test_has_differences_true():
    result = compare_envs(BASE_ENV, TARGET_ENV)
    assert result.has_differences is True


def test_has_differences_false():
    env = {"A": "1", "B": "2"}
    result = compare_envs(env, env.copy())
    assert result.has_differences is False


def test_custom_env_names():
    result = compare_envs(BASE_ENV, TARGET_ENV, base_name="dev", target_name="prod")
    assert result.base_name == "dev"
    assert result.target_name == "prod"
    assert "dev" in result.mismatched["DEBUG"]
    assert "prod" in result.mismatched["DEBUG"]


def test_is_secret_matches_keyword():
    assert _is_secret("DB_PASSWORD", ["password"]) is True
    assert _is_secret("API_KEY", ["key"]) is True


def test_is_secret_no_match():
    assert _is_secret("APP_NAME", ["password", "token"]) is False
