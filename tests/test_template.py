"""Tests for envdiff.template."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.template import (
    EnvTemplate,
    TemplateEntry,
    build_template,
    write_template,
    _make_placeholder,
)


SAMPLE_ENV = {
    "APP_NAME": "myapp",
    "DATABASE_URL": "postgres://user:pass@localhost/db",
    "SECRET_KEY": "supersecret",
    "PORT": "8080",
    "API_TOKEN": "tok_abc123",
}


# ---------------------------------------------------------------------------
# _make_placeholder
# ---------------------------------------------------------------------------

def test_placeholder_secret_contains_secret_label():
    result = _make_placeholder("SECRET_KEY", is_secret=True)
    assert "SECRET" in result


def test_placeholder_non_secret_uses_key_name():
    result = _make_placeholder("PORT", is_secret=False)
    assert "PORT" in result
    assert "SECRET" not in result


# ---------------------------------------------------------------------------
# build_template
# ---------------------------------------------------------------------------

def test_build_template_returns_env_template():
    tmpl = build_template(SAMPLE_ENV)
    assert isinstance(tmpl, EnvTemplate)


def test_build_template_key_count_matches_input():
    tmpl = build_template(SAMPLE_ENV)
    assert tmpl.key_count == len(SAMPLE_ENV)


def test_build_template_detects_secrets():
    tmpl = build_template(SAMPLE_ENV)
    secret_keys = {e.key for e in tmpl.entries if e.is_secret}
    assert "SECRET_KEY" in secret_keys
    assert "API_TOKEN" in secret_keys


def test_build_template_non_secret_detected():
    tmpl = build_template(SAMPLE_ENV)
    plain_keys = {e.key for e in tmpl.entries if not e.is_secret}
    assert "APP_NAME" in plain_keys
    assert "PORT" in plain_keys


def test_build_template_secret_value_replaced():
    tmpl = build_template(SAMPLE_ENV)
    entry = next(e for e in tmpl.entries if e.key == "SECRET_KEY")
    assert entry.placeholder != "supersecret"


def test_build_template_preserve_non_secrets_keeps_value():
    tmpl = build_template(SAMPLE_ENV, preserve_non_secrets=True)
    entry = next(e for e in tmpl.entries if e.key == "PORT")
    assert entry.placeholder == "8080"


def test_build_template_preserve_non_secrets_still_masks_secret():
    tmpl = build_template(SAMPLE_ENV, preserve_non_secrets=True)
    entry = next(e for e in tmpl.entries if e.key == "SECRET_KEY")
    assert entry.placeholder != "supersecret"


def test_build_template_source_path_stored():
    tmpl = build_template(SAMPLE_ENV, source_path=".env.production")
    assert tmpl.source_path == ".env.production"


def test_build_template_secret_count():
    tmpl = build_template(SAMPLE_ENV)
    assert tmpl.secret_count >= 2  # SECRET_KEY + API_TOKEN at minimum


# ---------------------------------------------------------------------------
# EnvTemplate.as_text / as_dict
# ---------------------------------------------------------------------------

def test_as_text_contains_all_keys():
    tmpl = build_template(SAMPLE_ENV)
    text = tmpl.as_text()
    for key in SAMPLE_ENV:
        assert key in text


def test_as_text_includes_source_comment_when_set():
    tmpl = build_template(SAMPLE_ENV, source_path=".env.prod")
    assert ".env.prod" in tmpl.as_text()


def test_as_text_no_source_comment_when_absent():
    tmpl = build_template(SAMPLE_ENV)
    assert "Generated from" not in tmpl.as_text()


def test_as_dict_returns_mapping():
    tmpl = build_template(SAMPLE_ENV)
    d = tmpl.as_dict()
    assert set(d.keys()) == set(SAMPLE_ENV.keys())


# ---------------------------------------------------------------------------
# write_template
# ---------------------------------------------------------------------------

def test_write_template_creates_file(tmp_path):
    tmpl = build_template(SAMPLE_ENV)
    out = tmp_path / ".env.template"
    result = write_template(tmpl, str(out))
    assert result.exists()


def test_write_template_content_matches_as_text(tmp_path):
    tmpl = build_template(SAMPLE_ENV)
    out = tmp_path / ".env.template"
    write_template(tmpl, str(out))
    assert out.read_text() == tmpl.as_text()
