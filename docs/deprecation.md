# Deprecation Detection

`envdiff.deprecation` lets you define a list of **deprecated key rules** and
scan any parsed `.env` mapping to find keys that should no longer be used.

## Quick start

```python
from envdiff.parser import parse_env_file
from envdiff.deprecation import DeprecationRule, check_deprecations

env = parse_env_file(".env")

rules = [
    DeprecationRule(
        old_key="OLD_DB_URL",
        new_key="DATABASE_URL",
        reason="renamed in v2",
    ),
    DeprecationRule(
        old_key="LEGACY_DEBUG",
        reason="use LOG_LEVEL=debug instead",
    ),
]

report = check_deprecations(env, rules)

if report.has_hits:
    for hit in report.hits:
        print(hit)  # [DEPRECATED] 'OLD_DB_URL' is deprecated; use 'DATABASE_URL' instead; (renamed in v2)
```

## API reference

### `DeprecationRule`

| Field | Type | Description |
|-------|------|-------------|
| `old_key` | `str` | The key that is deprecated. |
| `new_key` | `str \| None` | Replacement key name, if one exists. |
| `reason` | `str \| None` | Free-text explanation. |

```python
rule = DeprecationRule(old_key="API_TOKEN", new_key="API_KEY")
print(rule.message())
# "'API_TOKEN' is deprecated; use 'API_KEY' instead"
```

### `check_deprecations(env, rules) -> DeprecationReport`

Scans the provided `env` dictionary against the list of rules and returns a
`DeprecationReport`.

### `DeprecationReport`

| Attribute | Type | Description |
|-----------|------|-------------|
| `hits` | `list[DeprecationHit]` | All matched deprecated keys. |
| `scanned_keys` | `int` | Total number of keys examined. |
| `has_hits` | `bool` | `True` when at least one deprecated key was found. |
| `hit_count` | `int` | Number of deprecated keys found. |
| `as_dict()` | `dict` | Serialisable representation suitable for JSON export. |

## Integrating with the pipeline

You can run deprecation checks after `run_pipeline` to give a complete
picture of both drift *and* deprecated usage:

```python
from envdiff.pipeline import run_pipeline
from envdiff.deprecation import check_deprecations, DeprecationRule
from envdiff.parser import parse_env_file

pipeline = run_pipeline([".env.staging", ".env.production"])
env = parse_env_file(".env.staging")
report = check_deprecations(env, rules)

if pipeline.any_issues or report.has_hits:
    raise SystemExit(1)
```
