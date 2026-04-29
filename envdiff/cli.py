"""Command-line interface for envdiff."""

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_files
from envdiff.comparator import compare_envs
from envdiff.reporter import format_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments and report differences.",
    )
    parser.add_argument(
        "base",
        metavar="BASE",
        help="Path to the base .env file (e.g. .env.example)",
    )
    parser.add_argument(
        "target",
        metavar="TARGET",
        help="Path to the target .env file (e.g. .env.production)",
    )
    parser.add_argument(
        "--mask-secrets",
        action="store_true",
        default=False,
        help="Mask secret values in the report output",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        dest="output_format",
        help="Output format for the report (default: text)",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if differences are found",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    base_path = Path(args.base)
    target_path = Path(args.target)

    for path in (base_path, target_path):
        if not path.exists():
            print(f"envdiff: error: file not found: {path}", file=sys.stderr)
            return 2

    envs = parse_env_files(base_path, target_path)
    base_env = envs[str(base_path)]
    target_env = envs[str(target_path)]

    result = compare_envs(
        base_env,
        target_env,
        mask_secrets=args.mask_secrets,
    )

    report = format_report(result, output_format=args.output_format)
    print(report)

    if args.exit_code and result.has_differences():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
