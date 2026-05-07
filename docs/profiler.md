# envdiff profiler

The `envdiff.profiler` module analyses a single `.env` file and produces a
statistical profile of its key composition.

## Overview

| Concept | Description |
|---------|-------------|
| `EnvProfile` | Dataclass holding all statistics for one file |
| `profile_env(path)` | Build a profile from a single file path |
| `profile_many(paths)` | Build a list of profiles from multiple paths |

## Usage

```python
from envdiff.profiler import profile_env, profile_many

# Single file
profile = profile_env(".env.production")
print(profile.total_keys)    # 42
print(profile.secret_count)  # 8
print(profile.secret_ratio)  # 0.1905
print(profile.empty_keys)    # ['LOG_LEVEL', ...]

# Multiple files at once
profiles = profile_many([".env.staging", ".env.production"])
for p in profiles:
    print(p.path, p.secret_ratio)
```

## EnvProfile attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `path` | `str` | Source file path |
| `total_keys` | `int` | Total number of keys parsed |
| `secret_keys` | `List[str]` | Keys identified as secrets |
| `plain_keys` | `List[str]` | Keys not identified as secrets |
| `empty_keys` | `List[str]` | Keys whose value is an empty string |
| `duplicate_keys` | `List[str]` | Keys that appear more than once |
| `secret_count` | `int` | `len(secret_keys)` |
| `plain_count` | `int` | `len(plain_keys)` |
| `empty_count` | `int` | `len(empty_keys)` |
| `secret_ratio` | `float` | `secret_count / total_keys` (0 when empty) |

## Serialisation

Call `.as_dict()` to obtain a plain dictionary suitable for JSON export:

```python
import json
print(json.dumps(profile.as_dict(), indent=2))
```

## Secret detection

Key classification reuses the same `_is_secret` heuristic from
`envdiff.comparator`, so any key containing `SECRET`, `PASSWORD`, `TOKEN`,
`KEY`, or `AUTH` (case-insensitive) is counted as a secret.
