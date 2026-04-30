"""Validates .env file keys against a schema of required and optional keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set


@dataclass
class ValidationResult:
    """Result of validating an env mapping against a schema."""

    missing_required: List[str] = field(default_factory=list)
    unknown_keys: List[str] = field(default_factory=list)
    type_errors: Dict[str, str] = field(default_factory=dict)  # key -> message

    @property
    def is_valid(self) -> bool:
        return (
            not self.missing_required
            and not self.unknown_keys
            and not self.type_errors
        )

    def summary(self) -> str:
        """Return a human-readable summary of validation issues.

        Returns an empty string when there are no issues.
        """
        lines: List[str] = []
        if self.missing_required:
            lines.append(f"Missing required keys: {', '.join(self.missing_required)}")
        if self.unknown_keys:
            lines.append(f"Unknown keys: {', '.join(self.unknown_keys)}")
        for key, msg in sorted(self.type_errors.items()):
            lines.append(f"Type error for {key!r}: {msg}")
        return "\n".join(lines)


@dataclass
class KeySchema:
    """Schema definition for a single key."""

    required: bool = True
    expected_type: Optional[str] = None  # 'int', 'bool', 'url', or None
    description: str = ""


_BOOL_VALUES: Set[str] = {"true", "false", "1", "0", "yes", "no"}


def _validate_type(value: str, expected_type: str) -> Optional[str]:
    """Return an error message if *value* does not match *expected_type*."""
    if expected_type == "int":
        try:
            int(value)
        except ValueError:
            return f"expected integer, got {value!r}"
    elif expected_type == "bool":
        if value.lower() not in _BOOL_VALUES:
            return f"expected boolean (true/false/1/0/yes/no), got {value!r}"
    elif expected_type == "url":
        if not (value.startswith("http://") or value.startswith("https://")):
            return f"expected URL starting with http:// or https://, got {value!r}"
    return None


def validate_env(
    env: Dict[str, str],
    schema: Dict[str, KeySchema],
    *,
    allow_unknown: bool = True,
) -> ValidationResult:
    """Validate *env* against *schema*.

    Parameters
    ----------
    env:
        Parsed environment mapping.
    schema:
        Mapping of key name to :class:`KeySchema`.
    allow_unknown:
        When *False*, keys present in *env* but absent from *schema* are
        reported as unknown.
    """
    result = ValidationResult()

    for key, key_schema in schema.items():
        if key_schema.required and key not in env:
            result.missing_required.append(key)
        elif key in env and key_schema.expected_type is not None:
            error = _validate_type(env[key], key_schema.expected_type)
            if error:
                result.type_errors[key] = error

    if not allow_unknown:
        schema_keys = set(schema.keys())
        for key in env:
            if key not in schema_keys:
                result.unknown_keys.append(key)

    result.missing_required.sort()
    result.unknown_keys.sort()
    return result


def validate_many(
    envs: Dict[str, Dict[str, str]],
    schema: Dict[str, KeySchema],
    *,
    allow_unknown: bool = True,
) -> Dict[str, ValidationResult]:
    """Run :func:`validate_env` for each env in *envs*."""
    return {
        name: validate_env(env,
        schema, allow_unknown=allow_unknown)
        for name, env in envs.items()
    }
