"""CLI sub-command: generate a .env template from an existing env file."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.template import build_template, write_template


def build_template_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    description = "Generate a .env.template file from an existing .env file."
    if subparsers is not None:
        parser = subparsers.add_parser("template", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envdiff-template", description=description)

    parser.add_argument("env_file", help="Path to the source .env file.")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output path for the generated template (default: <env_file>.template).",
    )
    parser.add_argument(
        "--preserve-values",
        action="store_true",
        default=False,
        help="Keep non-secret values as-is instead of replacing with placeholders.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress informational output.",
    )
    return parser


def run_template_command(args: argparse.Namespace) -> int:
    """Execute the template sub-command. Returns an exit code."""
    source = Path(args.env_file)
    if not source.exists():
        print(f"error: file not found: {source}", file=sys.stderr)
        return 2

    output_path: str = args.output or str(source) + ".template"

    try:
        env = parse_env_file(str(source))
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not parse {source}: {exc}", file=sys.stderr)
        return 2

    template = build_template(
        env,
        source_path=str(source),
        preserve_non_secrets=args.preserve_values,
    )
    write_template(template, output_path)

    if not args.quiet:
        print(f"Template written to: {output_path}")
        print(f"  Total keys : {template.key_count}")
        print(f"  Secret keys: {template.secret_count}")

    return 0


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    parser = build_template_parser()
    args = parser.parse_args(argv)
    sys.exit(run_template_command(args))


if __name__ == "__main__":  # pragma: no cover
    main()
