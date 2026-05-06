"""Tests for envdiff.redactor."""

from __future__ import annotations

import pytest

from envdiff.redactor import DEFAULT_PLACEHOLDER, RedactedEnv, redact, redact_many


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PLAIN_ENV = {
    "APP_NAME": "myapp",
    "PORT": "8080",
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "s3cr3t",
    "API_TOKEN": "tok_abc123",
    "DEBUG": "true",
}


# ---------------------------------------------------------------------------
# redact()
# ---------------------------------------------------------------------------


def test_secret_key_is_redacted():
    result = redact(PLAIN_ENV)
    assert result.redacted["SECRET_KEY"] == DEFAULT_PLACEHOLDER


def test_api_token_is_redacted():
    result = redact(PLAIN_ENV)
    assert result.redacted["API_TOKEN"] == DEFAULT_PLACEHOLDER


def test_database_url_is_redacted():
    result = redact(PLAIN_ENV)
    assert result.redacted["DATABASE_URL"] == DEFAULT_PLACEHOLDER


def test_plain_keys_are_preserved():
    result = redact(PLAIN_ENV)
    assert result.redacted["APP_NAME"] == "myapp"
    assert result.redacted["PORT"] == "8080"
    assert result.redacted["DEBUG"] == "true"


def test_original_keys_list_matches_input():
    result = redact(PLAIN_ENV)
    assert result.original_keys == list(PLAIN_ENV.keys())


def test_redacted_keys_contains_only_secrets():
    result = redact(PLAIN_ENV)
    for k in result.redacted_keys:
        assert result.redacted[k] == DEFAULT_PLACEHOLDER


def test_total_keys_count():
    result = redact(PLAIN_ENV)
    assert result.total_keys == len(PLAIN_ENV)


def test_total_redacted_count():
    result = redact(PLAIN_ENV)
    # SECRET_KEY, API_TOKEN, DATABASE_URL are secrets by heuristic
    assert result.total_redacted >= 3


def test_custom_placeholder():
    result = redact(PLAIN_ENV, placeholder="<hidden>")
    assert result.redacted["SECRET_KEY"] == "<hidden>"


def test_extra_patterns_redact_additional_keys():
    env = {"MY_INTERNAL_CERT": "cert-data", "HOST": "localhost"}
    result = redact(env, extra_patterns=["cert"])
    assert result.redacted["MY_INTERNAL_CERT"] == DEFAULT_PLACEHOLDER
    assert result.redacted["HOST"] == "localhost"


def test_empty_env_returns_empty_redacted_env():
    result = redact({})
    assert isinstance(result, RedactedEnv)
    assert result.total_keys == 0
    assert result.total_redacted == 0


# ---------------------------------------------------------------------------
# redact_many()
# ---------------------------------------------------------------------------


def test_redact_many_returns_all_labels():
    envs = {"staging": PLAIN_ENV, "production": PLAIN_ENV}
    results = redact_many(envs)
    assert set(results.keys()) == {"staging", "production"}


def test_redact_many_each_result_is_redacted_env():
    envs = {"dev": PLAIN_ENV}
    results = redact_many(envs)
    assert isinstance(results["dev"], RedactedEnv)


def test_redact_many_secrets_hidden_per_env():
    envs = {"a": {"PASSWORD": "hunter2", "NAME": "alice"}}
    results = redact_many(envs)
    assert results["a"].redacted["PASSWORD"] == DEFAULT_PLACEHOLDER
    assert results["a"].redacted["NAME"] == "alice"
