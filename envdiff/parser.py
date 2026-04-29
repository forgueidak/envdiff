"""Parser module for reading and parsing .env files."""

import os
import re
from typing import Dict, Optional


ENV_LINE_PATTERN = re.compile(
    r'^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$'
)

COMMENT_PATTERN = re.compile(r'^\s*#')


def parse_env_file(filepath: str) -> Dict[str, str]:
    """
    Parse a .env file and return a dictionary of key-value pairs.

    Args:
        filepath: Path to the .env file.

    Returns:
        Dictionary mapping environment variable names to their values.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file contains invalid syntax.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Environment file not found: {filepath}")

    env_vars: Dict[str, str] = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_number, line in enumerate(f, start=1):
            line = line.rstrip('\n')

            # Skip empty lines and comments
            if not line.strip() or COMMENT_PATTERN.match(line):
                continue

            match = ENV_LINE_PATTERN.match(line)
            if not match:
                raise ValueError(
                    f"Invalid syntax at line {line_number} in '{filepath}': {line!r}"
                )

            key = match.group('key')
            value = _strip_quotes(match.group('value').strip())
            env_vars[key] = value

    return env_vars


def _strip_quotes(value: str) -> str:
    """
    Remove surrounding single or double quotes from a value.

    Args:
        value: The raw string value from the .env file.

    Returns:
        The value with surrounding quotes removed, if present.
    """
    if len(value) >= 2:
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
    return value


def parse_env_files(*filepaths: str) -> Dict[str, Dict[str, str]]:
    """
    Parse multiple .env files and return a mapping of filepath to key-value pairs.

    Args:
        *filepaths: One or more paths to .env files.

    Returns:
        Dictionary mapping each filepath to its parsed environment variables.
    """
    return {fp: parse_env_file(fp) for fp in filepaths}
