"""CLI sub-commands: snapshot save / snapshot diff."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.snapshot import capture, load_snapshot, save_snapshot, snapshots_equal
from envdiff.comparator import compare_envs
from envdiff.reporter import format_report


def build_snapshot_parser(parent: "argparse._SubParsersAction") -> None:  # noqa: F821
    sp = parent.add_parser("snapshot", help="Capture or compare env snapshots")
    sub = sp.add_subparsers(dest="snapshot_cmd", required=True)

    # snapshot save
    save_p = sub.add_parser("save", help="Capture and persist a snapshot")
    save_p.add_argument("env_file", help="Path to the .env file")
    save_p.add_argument("output", help="Destination JSON file")
    save_p.add_argument("--label", default=None, help="Human-readable label")

    # snapshot diff
    diff_p = sub.add_parser("diff", help="Diff two saved snapshots")
    diff_p.add_argument("snapshot_a", help="First snapshot JSON")
    diff_p.add_argument("snapshot_b", help="Second snapshot JSON")
    diff_p.add_argument(
        "--format", choices=["text", "json", "markdown"], default="text"
    )
    diff_p.add_argument("--mask-secrets", action="store_true", default=False)


def run_snapshot_command(args: argparse.Namespace) -> int:
    """Dispatch snapshot sub-commands; return exit code."""
    if args.snapshot_cmd == "save":
        snap = capture(args.env_file, label=args.label)
        save_snapshot(snap, args.output)
        print(f"Snapshot saved to {args.output} ({snap.key_count()} keys)")
        return 0

    if args.snapshot_cmd == "diff":
        a = load_snapshot(args.snapshot_a)
        b = load_snapshot(args.snapshot_b)

        if snapshots_equal(a, b):
            print("Snapshots are identical.")
            return 0

        result = compare_envs(a.keys, b.keys, mask_secrets=args.mask_secrets)
        report = format_report(result, fmt=args.format)
        print(report)
        return 1

    print(f"Unknown snapshot sub-command: {args.snapshot_cmd}", file=sys.stderr)
    return 2
