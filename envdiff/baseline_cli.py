"""CLI sub-commands for baseline management: save and compare."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.comparator import compare_envs
from envdiff.parser import parse_env_files
from envdiff.baseline import (
    diff_against_baseline,
    load_baseline,
    save_baseline,
)
from envdiff.reporter import format_report


def build_baseline_parser(parent: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register 'baseline' sub-commands onto *parent*."""
    bp = parent.add_parser("baseline", help="Manage diff baselines")
    sub = bp.add_subparsers(dest="baseline_cmd", required=True)

    # save
    save_p = sub.add_parser("save", help="Save current diff as baseline")
    save_p.add_argument("base", help="Base .env file")
    save_p.add_argument("target", help="Target .env file")
    save_p.add_argument(
        "--output", "-o", default=".envdiff_baseline.json",
        help="Destination baseline file (default: .envdiff_baseline.json)",
    )

    # compare
    cmp_p = sub.add_parser("compare", help="Compare current diff against baseline")
    cmp_p.add_argument("base", help="Base .env file")
    cmp_p.add_argument("target", help="Target .env file")
    cmp_p.add_argument(
        "--baseline", "-b", default=".envdiff_baseline.json",
        help="Baseline file to compare against",
    )
    cmp_p.add_argument(
        "--format", "-f", choices=["text", "json", "markdown"],
        default="text", dest="fmt",
    )
    cmp_p.add_argument(
        "--fail-on-new", action="store_true",
        help="Exit 1 when new issues are found beyond the baseline",
    )


def run_baseline_command(args: argparse.Namespace) -> int:
    """Dispatch baseline sub-command; returns exit code."""
    envs = parse_env_files([args.base, args.target])
    base_env, target_env = envs[args.base], envs[args.target]
    current = compare_envs(base_env, target_env)

    if args.baseline_cmd == "save":
        save_baseline(current, args.output)
        print(f"Baseline saved to {args.output}")
        return 0

    # compare
    if not Path(args.baseline).exists():
        print(f"Baseline file not found: {args.baseline}", file=sys.stderr)
        return 2

    stored = load_baseline(args.baseline)
    delta = diff_against_baseline(current, stored)
    report = format_report(delta, fmt=args.fmt, mask_secrets=False)
    print(report)

    if args.fail_on_new and (
        delta.missing_in_target or delta.missing_in_base or delta.mismatched
    ):
        return 1
    return 0
