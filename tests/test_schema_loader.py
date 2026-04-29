"""Tests for envdiff.schema_loader."""

import json
import textwrap
from pathlib import Path

import pytest

from envdiff.schema_loader import load_schema, load_schema_json
from envdiff.validator import KeySchema


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def schema_json(tmp_path: Path) -> Path:
    data = {
        "DATABASE_URL": {"required": True, "type": "url", "description": "DB conn"},
        "PORT": {"required": True, "type": "int"},
        "DEBUG": {"required": False, "type": "bool"},
        "APP_NAME": {"required": True},
    }
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


@pytest.fixture()
def schema_toml(tmp_path: Path) -> Path:
    content = textwrap.dedent("""
        [DATABASE_URL]
        required = true
        type = "url"
        description = "DB conn"

        [PORT]
        required = true
        type = "int"

        [DEBUG]
        required = false
        type = "bool"

        [APP_NAME]
        required = true
    """)
    p = tmp_path / "schema.toml"
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# JSON loader
# ---------------------------------------------------------------------------


def test_json_loads_all_keys(schema_json: Path):
    schema = load_schema_json(schema_json)
    assert set(schema.keys()) == {"DATABASE_URL", "PORT", "DEBUG", "APP_NAME"}


def test_json_required_flag(schema_json: Path):
    schema = load_schema_json(schema_json)
    assert schema["DATABASE_URL"].required is True
    assert schema["DEBUG"].required is False


def test_json_type_field(schema_json: Path):
    schema = load_schema_json(schema_json)
    assert schema["DATABASE_URL"].expected_type == "url"
    assert schema["PORT"].expected_type == "int"
    assert schema["DEBUG"].expected_type == "bool"


def test_json_no_type_gives_none(schema_json: Path):
    schema = load_schema_json(schema_json)
    assert schema["APP_NAME"].expected_type is None


def test_json_description(schema_json: Path):
    schema = load_schema_json(schema_json)
    assert schema["DATABASE_URL"].description == "DB conn"


def test_json_invalid_root_type(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        load_schema_json(p)


# ---------------------------------------------------------------------------
# auto-detect via load_schema
# ---------------------------------------------------------------------------


def test_load_schema_json_dispatch(schema_json: Path):
    schema = load_schema(schema_json)
    assert isinstance(schema["PORT"], KeySchema)


def test_load_schema_unsupported_extension(tmp_path: Path):
    p = tmp_path / "schema.yaml"
    p.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported"):
        load_schema(p)


# ---------------------------------------------------------------------------
# TOML loader (skipped when tomllib/tomli unavailable)
# ---------------------------------------------------------------------------


def test_toml_loads_all_keys(schema_toml: Path):
    pytest.importorskip("tomllib", reason="tomllib not available")
    from envdiff.schema_loader import load_schema_toml

    schema = load_schema_toml(schema_toml)
    assert set(schema.keys()) == {"DATABASE_URL", "PORT", "DEBUG", "APP_NAME"}
    assert schema["PORT"].expected_type == "int"
    assert schema["DEBUG"].required is False
