"""CLI entry-point for the env-merge sub-command."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from envdiff.merger import merge_env_files
from envdiff.merger_reporter import format_merge_report


def build_merger_parser(
    parent: Optional[argparse.ArgumentParser] = None,
) -> argparse.ArgumentParser:
    parser = parent or argparse.ArgumentParser(
        prog="envdiff merge",
        description="Merge multiple .env files (last file wins on conflicts).",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files to merge in order.",
    )
    parser.add_argument(
        "--labels",
        nargs="+",
        metavar="LABEL",
        help="Optional labels for each file (same order).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        dest="fmt",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--fail-on-conflict",
        action="store_true",
        help="Exit with code 1 if any key conflicts are found.",
    )
    return parser


def run_merger_command(args: argparse.Namespace) -> int:
    paths: List[Path] = [Path(f) for f in args.files]
    labels = args.labels if hasattr(args, "labels") else None

    try:
        result = merge_env_files(paths, labels=labels)
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(format_merge_report(result, fmt=args.fmt))

    if getattr(args, "fail_on_conflict", False) and result.has_conflicts:
        return 1
    return 0


def main(argv: Optional[List[str]] = None) -> None:  # pragma: no cover
    parser = build_merger_parser()
    args = parser.parse_args(argv)
    sys.exit(run_merger_command(args))
