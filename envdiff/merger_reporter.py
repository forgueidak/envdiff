"""Format a :class:`MergeResult` as text, JSON, or Markdown."""
from __future__ import annotations

import json
from typing import Literal

from envdiff.merger import MergeResult

Format = Literal["text", "json", "markdown"]


def format_merge_report(result: MergeResult, fmt: Format = "text") -> str:
    """Return a formatted report for *result*."""
    if fmt == "json":
        return _format_json(result)
    if fmt == "markdown":
        return _format_markdown(result)
    return _format_text(result)


def _format_text(result: MergeResult) -> str:
    lines = ["Merge Report", "=" * 40]
    lines.append(f"Sources ({len(result.sources)}):")
    for src in result.sources:
        lines.append(f"  - {src}")
    lines.append(f"Total merged keys : {len(result.merged)}")
    lines.append(f"Conflicts         : {result.conflict_count}")
    if result.has_conflicts:
        lines.append("")
        lines.append("Conflicts:")
        for c in result.conflicts:
            lines.append(f"  {c.key}")
            lines.append(f"    was : '{c.original_value}' ({c.original_source})")
            lines.append(f"    now : '{c.winning_value}' ({c.winning_source})")
    return "\n".join(lines)


def _format_json(result: MergeResult) -> str:
    return json.dumps(result.as_dict(), indent=2)


def _format_markdown(result: MergeResult) -> str:
    lines = ["# Merge Report", ""]
    lines.append("## Sources")
    for src in result.sources:
        lines.append(f"- `{src}`")
    lines.append("")
    lines.append(f"**Total merged keys:** {len(result.merged)}  ")
    lines.append(f"**Conflicts:** {result.conflict_count}")
    if result.has_conflicts:
        lines.append("")
        lines.append("## Conflicts")
        lines.append("| Key | Original value | Source | Winning value | Source |")
        lines.append("|-----|---------------|--------|---------------|--------|")
        for c in result.conflicts:
            lines.append(
                f"| `{c.key}` | `{c.original_value}` | {c.original_source} "
                f"| `{c.winning_value}` | {c.winning_source} |"
            )
    return "\n".join(lines)
