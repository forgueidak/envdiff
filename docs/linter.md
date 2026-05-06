# envdiff Linter

The `envdiff.linter` module inspects individual `.env` files for style and
correctness problems **before** running a cross-environment comparison.

---

## Quick Start

```python
from envdiff.linter import lint_env_file, lint_many

# Single file
result = lint_env_file(".env.production")
if not result.is_clean:
    for issue in result.issues:
        print(issue)  # Line 3: [W001] db_host — Key is not UPPER_SNAKE_CASE

# Multiple files
results = lint_many([".env.staging", ".env.production"])
```

---

## Lint Codes

| Code  | Severity | Description                              |
|-------|----------|------------------------------------------|
| E001  | Error    | Line is not a valid `KEY=VALUE` pair     |
| E002  | Error    | Empty key name                           |
| E003  | Error    | Key contains whitespace                  |
| E004  | Error    | Unmatched quote in value                 |
| W001  | Warning  | Key is not `UPPER_SNAKE_CASE`            |
| W002  | Warning  | Value is empty                           |

---

## API Reference

### `lint_env_file(path: str) -> LintResult`

Runs all lint checks against a single `.env` file.  Returns a `LintResult`.

### `lint_many(paths: List[str]) -> List[LintResult]`

Convenience wrapper that calls `lint_env_file` for each path.

---

## Data Classes

### `LintIssue`

| Field         | Type  | Description                        |
|---------------|-------|------------------------------------|
| `line_number` | `int` | 1-based line number in the file    |
| `key`         | `str` | The key name (or `"?"` if unknown) |
| `code`        | `str` | Lint code (e.g. `"W001"`)          |
| `message`     | `str` | Human-readable description         |

`str(issue)` produces a formatted summary, e.g.:
```
Line 4: [E004] MY_KEY — Unmatched quote in value
```

### `LintResult`

| Attribute / Method          | Description                                      |
|-----------------------------|--------------------------------------------------|
| `path`                      | Path of the linted file                          |
| `issues`                    | List of `LintIssue` objects                      |
| `is_clean`                  | `True` when there are no issues                  |
| `issue_count`               | Number of issues found                           |
| `by_code(code)` → `list`   | Filter issues by lint code                       |

---

## Integration with the Pipeline

Run the linter before `run_pipeline` to surface formatting problems early:

```python
from envdiff.linter import lint_many
from envdiff.pipeline import run_pipeline

paths = [".env", ".env.staging", ".env.production"]

for lr in lint_many(paths):
    if not lr.is_clean:
        print(f"{lr.path}: {lr.issue_count} lint issue(s)")
        for issue in lr.issues:
            print(f"  {issue}")

pipeline = run_pipeline(paths)
```
