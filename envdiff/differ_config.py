"""Load DiffOptions from a TOML or JSON config file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from envdiff.differ import DiffOptions

_DEFAULTS: Dict[str, Any] = {
    "mask_secrets": True,
    "include_patterns": [],
    "exclude_patterns": [],
    "label_base": "base",
    "label_target": "target",
}


def _load_raw(path: Path) -> Dict[str, Any]:
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")

    if suffix == ".json":
        return json.loads(text)

    if suffix == ".toml":
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore[no-redef]
            except ImportError as exc:  # pragma: no cover
                raise ImportError(
                    "tomli is required for TOML support on Python < 3.11"
                ) from exc
        return tomllib.loads(text)

    raise ValueError(f"Unsupported config format: {suffix!r}. Use .json or .toml.")


def load_diff_options(config_path: str | Path) -> DiffOptions:
    """Parse a JSON or TOML config file and return a :class:`DiffOptions` instance."""
    path = Path(config_path)
    raw = _load_raw(path)

    # Merge with defaults so missing keys are handled gracefully
    merged = {**_DEFAULTS, **raw}

    return DiffOptions(
        mask_secrets=bool(merged["mask_secrets"]),
        include_patterns=list(merged["include_patterns"]),
        exclude_patterns=list(merged["exclude_patterns"]),
        label_base=str(merged["label_base"]),
        label_target=str(merged["label_target"]),
    )
