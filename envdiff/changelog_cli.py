"""CLI sub-commands for managing the env diff changelog."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.changelog import Changelog, load_changelog, record_entry, save_changelog
from envdiff.comparator import compare_envs
from envdiff.parser import parse_env_files


def build_changelog_parser(parent: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = parent.add_parser("changelog", help="Manage env diff changelog")
    sub = p.add_subparsers(dest="changelog_cmd", required=True)

    rec = sub.add_parser("record", help="Record a diff into the changelog")
    rec.add_argument("base", help="Base .env file")
    rec.add_argument("target", help="Target .env file")
    rec.add_argument(
        "--changelog", default=".envdiff_changelog.json", help="Changelog file path"
    )
    rec.add_argument("--mask-secrets", action="store_true", default=False)

    show = sub.add_parser("show", help="Print the changelog")
    show.add_argument(
        "--changelog", default=".envdiff_changelog.json", help="Changelog file path"
    )
    show.add_argument(
        "--limit", type=int, default=0, help="Max entries to show (0 = all)"
    )


def _cmd_record(args: argparse.Namespace) -> int:
    envs = parse_env_files([args.base, args.target])
    base_env, target_env = envs[0], envs[1]
    result = compare_envs(base_env, target_env, mask_secrets=args.mask_secrets)

    cl_path = Path(args.changelog)
    cl = load_changelog(cl_path) if cl_path.exists() else Changelog()
    entry = record_entry(result, args.base, args.target)
    cl.add(entry)
    save_changelog(cl, cl_path)
    print(f"Recorded entry ({entry.total_issues} issue(s)) → {cl_path}")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    cl_path = Path(args.changelog)
    if not cl_path.exists():
        print(f"No changelog found at {cl_path}", file=sys.stderr)
        return 1
    cl = load_changelog(cl_path)
    entries = cl.entries
    if args.limit > 0:
        entries = entries[-args.limit :]
    if not entries:
        print("Changelog is empty.")
        return 0
    for e in entries:
        print(
            f"[{e.timestamp}] {e.base} → {e.target}  "
            f"issues={e.total_issues} "
            f"(missing_in_target={len(e.missing_in_target)}, "
            f"missing_in_base={len(e.missing_in_base)}, "
            f"mismatched={len(e.mismatched)})"
        )
    return 0


def run_changelog_command(args: argparse.Namespace) -> int:
    if args.changelog_cmd == "record":
        return _cmd_record(args)
    if args.changelog_cmd == "show":
        return _cmd_show(args)
    return 1
