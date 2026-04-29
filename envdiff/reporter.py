"""Formats and outputs diff results for human-readable or machine-readable consumption."""

from typing import Literal
from envdiff.comparator import DiffResult

OutputFormat = Literal["text", "json", "markdown"]


def format_report(result: DiffResult, fmt: OutputFormat = "text") -> str:
    """Format a DiffResult into a string report.

    Args:
        result: The diff result to format.
        fmt: Output format — 'text', 'json', or 'markdown'.

    Returns:
        A formatted string report.
    """
    if fmt == "json":
        return _format_json(result)
    elif fmt == "markdown":
        return _format_markdown(result)
    else:
        return _format_text(result)


def _format_text(result: DiffResult) -> str:
    lines = []

    if result.missing_in_target:
        lines.append("Missing in target:")
        for key in sorted(result.missing_in_target):
            lines.append(f"  - {key}")

    if result.missing_in_base:
        lines.append("Missing in base:")
        for key in sorted(result.missing_in_base):
            lines.append(f"  + {key}")

    if result.mismatched:
        lines.append("Mismatched values:")
        for key, (base_val, target_val) in sorted(result.mismatched.items()):
            lines.append(f"  ~ {key}")
            lines.append(f"      base:   {base_val}")
            lines.append(f"      target: {target_val}")

    if not lines:
        lines.append("No differences found.")

    return "\n".join(lines)


def _format_json(result: DiffResult) -> str:
    import json

    data = {
        "missing_in_target": sorted(result.missing_in_target),
        "missing_in_base": sorted(result.missing_in_base),
        "mismatched": {
            key: {"base": base_val, "target": target_val}
            for key, (base_val, target_val) in sorted(result.mismatched.items())
        },
    }
    return json.dumps(data, indent=2)


def _format_markdown(result: DiffResult) -> str:
    lines = ["# Env Diff Report", ""]

    lines.append("## Missing in Target")
    if result.missing_in_target:
        for key in sorted(result.missing_in_target):
            lines.append(f"- `{key}`")
    else:
        lines.append("_None_")

    lines.append("")
    lines.append("## Missing in Base")
    if result.missing_in_base:
        for key in sorted(result.missing_in_base):
            lines.append(f"- `{key}`")
    else:
        lines.append("_None_")

    lines.append("")
    lines.append("## Mismatched Values")
    if result.mismatched:
        for key, (base_val, target_val) in sorted(result.mismatched.items()):
            lines.append(f"- `{key}`: `{base_val}` → `{target_val}`")
    else:
        lines.append("_None_")

    return "\n".join(lines)
