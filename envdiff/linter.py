"""Lints .env files for common style and correctness issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envdiff.parser import parse_env_file


@dataclass
class LintIssue:
    line_number: int
    key: str
    code: str
    message: str

    def __str__(self) -> str:
        return f"Line {self.line_number}: [{self.code}] {self.key} — {self.message}"


@dataclass
class LintResult:
    path: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.issues) == 0

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    def by_code(self, code: str) -> List[LintIssue]:
        return [i for i in self.issues if i.code == code]


def lint_env_file(path: str) -> LintResult:
    """Run all lint checks against a single .env file."""
    result = LintResult(path=path)
    raw_lines = Path(path).read_text(encoding="utf-8").splitlines()

    for lineno, raw in enumerate(raw_lines, start=1):
        stripped = raw.strip()

        # Skip blank lines and comments
        if not stripped or stripped.startswith("#"):
            continue

        if "=" not in stripped:
            result.issues.append(
                LintIssue(lineno, "?", "E001", "Line is not a valid KEY=VALUE pair")
            )
            continue

        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip()

        if not key:
            result.issues.append(
                LintIssue(lineno, "", "E002", "Empty key name")
            )

        if key != key.upper():
            result.issues.append(
                LintIssue(lineno, key, "W001", "Key is not UPPER_SNAKE_CASE")
            )

        if " " in key:
            result.issues.append(
                LintIssue(lineno, key, "E003", "Key contains whitespace")
            )

        if value == "":
            result.issues.append(
                LintIssue(lineno, key, "W002", "Value is empty")
            )

        if (value.startswith('"') and not value.endswith('"')) or (
            value.startswith("'") and not value.endswith("'")
        ):
            result.issues.append(
                LintIssue(lineno, key, "E004", "Unmatched quote in value")
            )

    return result


def lint_many(paths: List[str]) -> List[LintResult]:
    """Lint multiple .env files and return all results."""
    return [lint_env_file(p) for p in paths]
