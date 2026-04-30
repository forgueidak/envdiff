"""Export diff results to various file formats (JSON, Markdown, CSV)."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Union

from envdiff.comparator import DiffResult
from envdiff.reporter import _format_json, _format_markdown


SUPPORTED_FORMATS = ("json", "markdown", "csv")


def export_result(
    result: DiffResult,
    fmt: str,
    mask_secrets: bool = False,
) -> str:
    """Render *result* as a string in the requested format.

    Parameters
    ----------
    result:
        The diff result produced by :func:`~envdiff.comparator.compare_envs`.
    fmt:
        One of ``'json'``, ``'markdown'``, or ``'csv'``.
    mask_secrets:
        When *True* secret values are replaced with ``***``.

    Returns
    -------
    str
        Formatted string ready to be written to a file or stdout.
    """
    fmt = fmt.lower()
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")

    if fmt == "json":
        return _format_json(result, mask_secrets=mask_secrets)
    if fmt == "markdown":
        return _format_markdown(result, mask_secrets=mask_secrets)
    return _format_csv(result, mask_secrets=mask_secrets)


def export_to_file(
    result: DiffResult,
    path: Union[str, Path],
    fmt: str | None = None,
    mask_secrets: bool = False,
) -> Path:
    """Write *result* to *path*, inferring *fmt* from the file extension when omitted."""
    path = Path(path)
    if fmt is None:
        ext = path.suffix.lstrip(".")
        fmt = "markdown" if ext in ("md", "markdown") else ext
    content = export_result(result, fmt=fmt, mask_secrets=mask_secrets)
    path.write_text(content, encoding="utf-8")
    return path


def _format_csv(result: DiffResult, mask_secrets: bool = False) -> str:
    """Render *result* as CSV with columns: type, key, base_value, target_value."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["type", "key", "base_value", "target_value"])

    for key in sorted(result.missing_in_target):
        writer.writerow(["missing_in_target", key, "", ""])

    for key in sorted(result.missing_in_base):
        writer.writerow(["missing_in_base", key, "", ""])

    for key, (base_val, target_val) in sorted(result.mismatched.items()):
        if mask_secrets and result.masked_keys and key in result.masked_keys:
            base_val = target_val = "***"
        writer.writerow(["mismatched", key, base_val, target_val])

    return buf.getvalue()
