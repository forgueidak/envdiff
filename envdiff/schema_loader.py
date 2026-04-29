"""Load a KeySchema mapping from a TOML or JSON schema file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from envdiff.validator import KeySchema


def _parse_key_entry(entry: dict) -> KeySchema:
    """Convert a raw dict entry into a :class:`KeySchema`."""
    return KeySchema(
        required=bool(entry.get("required", True)),
        expected_type=entry.get("type") or None,
        description=entry.get("description", ""),
    )


def load_schema_json(path: str | Path) -> Dict[str, KeySchema]:
    """Load a schema from a JSON file.

    Expected format::

        {
          "DATABASE_URL": {"required": true, "type": "url", "description": "..."},
          "PORT": {"required": true, "type": "int"},
          "DEBUG": {"required": false, "type": "bool"}
        }
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Schema file must contain a JSON object, got {type(data).__name__}")
    return {key: _parse_key_entry(value) for key, value in data.items()}


def load_schema_toml(path: str | Path) -> Dict[str, KeySchema]:
    """Load a schema from a TOML file.

    Expected format::

        [DATABASE_URL]
        required = true
        type = "url"
        description = "Primary database connection string"

        [PORT]
        required = true
        type = "int"
    """
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore[no-redef]
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "TOML support requires Python 3.11+ or 'tomli' package."
            ) from exc

    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    return {key: _parse_key_entry(value) for key, value in data.items()}


def load_schema(path: str | Path) -> Dict[str, KeySchema]:
    """Auto-detect format from file extension and load the schema."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".json":
        return load_schema_json(path)
    if suffix == ".toml":
        return load_schema_toml(path)
    raise ValueError(f"Unsupported schema file format: {suffix!r} (use .json or .toml)")
