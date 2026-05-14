"""Generate .env.template files from parsed env data, stripping secret values."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.comparator import _is_secret


@dataclass
class TemplateEntry:
    key: str
    placeholder: str
    is_secret: bool
    original_value: Optional[str] = None

    def render(self) -> str:
        """Return the key=placeholder line for the template."""
        return f"{self.key}={self.placeholder}"


@dataclass
class EnvTemplate:
    entries: List[TemplateEntry] = field(default_factory=list)
    source_path: Optional[str] = None

    @property
    def key_count(self) -> int:
        return len(self.entries)

    @property
    def secret_count(self) -> int:
        return sum(1 for e in self.entries if e.is_secret)

    def as_text(self) -> str:
        """Render the full template as a string."""
        lines = []
        if self.source_path:
            lines.append(f"# Generated from: {self.source_path}")
            lines.append("")
        for entry in self.entries:
            lines.append(entry.render())
        return "\n".join(lines) + "\n"

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.placeholder for e in self.entries}


def _make_placeholder(key: str, is_secret: bool) -> str:
    if is_secret:
        return f"<{key.upper()}_SECRET>"
    return f"<{key.upper()}>"


def build_template(
    env: Dict[str, str],
    source_path: Optional[str] = None,
    preserve_non_secrets: bool = False,
) -> EnvTemplate:
    """Build an EnvTemplate from a parsed env dict.

    Args:
        env: Mapping of key -> value.
        source_path: Optional label for the source file.
        preserve_non_secrets: If True, non-secret values are kept as-is.
    """
    entries: List[TemplateEntry] = []
    for key, value in env.items():
        secret = _is_secret(key)
        if preserve_non_secrets and not secret:
            placeholder = value
        else:
            placeholder = _make_placeholder(key, secret)
        entries.append(
            TemplateEntry(
                key=key,
                placeholder=placeholder,
                is_secret=secret,
                original_value=value,
            )
        )
    return EnvTemplate(entries=entries, source_path=source_path)


def write_template(template: EnvTemplate, output_path: str) -> Path:
    """Write the rendered template to *output_path* and return the Path."""
    path = Path(output_path)
    path.write_text(template.as_text(), encoding="utf-8")
    return path
