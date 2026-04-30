# Baseline Snapshots

The **baseline** feature lets you capture the current diff state between two `.env` files and later compare against it to surface only *new* regressions.

## Concepts

| Term | Meaning |
|------|---------|
| **Baseline** | A JSON snapshot of a `DiffResult` saved at a known-good point in time. |
| **Delta** | The set of issues present in the *current* diff that were **not** present in the baseline. |

## Python API

```python
from envdiff.baseline import save_baseline, load_baseline, diff_against_baseline
from envdiff.comparator import compare_envs
from envdiff.parser import parse_env_files

envs = parse_env_files(["staging.env", "production.env"])
result = compare_envs(envs["staging.env"], envs["production.env"])

# Save snapshot
save_baseline(result, ".envdiff_baseline.json")

# Later — check for new issues only
stored = load_baseline(".envdiff_baseline.json")
delta = diff_against_baseline(result, stored)
if delta.missing_in_target or delta.mismatched:
    print("New issues detected since baseline!")
```

## CLI

### Save a baseline

```bash
python -m envdiff baseline save staging.env production.env \
    --output .envdiff_baseline.json
```

### Compare against a baseline

```bash
# Print only new issues (text format)
python -m envdiff baseline compare staging.env production.env \
    --baseline .envdiff_baseline.json --format text

# Exit 1 when new issues are found (useful in CI)
python -m envdiff baseline compare staging.env production.env \
    --baseline .envdiff_baseline.json --fail-on-new
```

## Baseline file format

```json
{
  "version": 1,
  "diff": {
    "missing_in_target": ["KEY_A"],
    "missing_in_base": [],
    "mismatched": {
      "DB_HOST": {"base": "localhost", "target": "prod.db"}
    }
  }
}
```

> **Tip:** Commit `.envdiff_baseline.json` to version control so your CI pipeline can detect newly introduced mismatches automatically.
