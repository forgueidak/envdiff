# Annotator

The `envdiff.annotator` module enriches a diff result by attaching a **status
label** to every key that appears in either the base or target env file.

## Status labels

| Status | Meaning |
|---|---|
| `ok` | Key exists in both files with identical values |
| `missing_in_target` | Key present in base but absent from target |
| `missing_in_base` | Key present in target but absent from base |
| `mismatched` | Key exists in both files but values differ |

## Quick start

```python
from envdiff.parser import parse_env_file
from envdiff.comparator import compare_envs
from envdiff.annotator import annotate

base   = parse_env_file(".env.development")
target = parse_env_file(".env.production")

result = compare_envs(base, target)
diff   = annotate(base, target, result,
                  base_path=".env.development",
                  target_path=".env.production")

for line in diff.lines:
    print(f"{line.status:25s} {line.key}")
```

## API

### `annotate(base, target, result, base_path, target_path) -> AnnotatedDiff`

Returns an `AnnotatedDiff` whose `.lines` list contains one `AnnotatedLine`
per unique key, sorted alphabetically.

### `AnnotatedDiff`

| Attribute | Type | Description |
|---|---|---|
| `base_path` | `str` | Label for the base file |
| `target_path` | `str` | Label for the target file |
| `lines` | `list[AnnotatedLine]` | Annotated key lines |
| `has_issues` | `bool` | `True` if any line is not `ok` |
| `by_status(status)` | `list[AnnotatedLine]` | Filter lines by status string |

### `AnnotatedLine`

| Attribute | Type | Description |
|---|---|---|
| `key` | `str` | Environment variable name |
| `value` | `str \| None` | Value from base (or target for `missing_in_base`) |
| `status` | `str` | One of the four status labels |
| `base_value` | `str \| None` | Raw value from base file |
| `target_value` | `str \| None` | Raw value from target file |
| `is_ok` | `bool` | Shorthand for `status == 'ok'` |

## Integration with the pipeline

`annotate` accepts a `DiffResult` produced by `compare_envs`, so it slots
naturally into an existing `run_diff` / `run_pipeline` workflow:

```python
from envdiff.differ import run_diff, DiffOptions
from envdiff.annotator import annotate

opts = DiffOptions(mask_secrets=True)
run  = run_diff(".env", ".env.staging", opts)

diff = annotate(
    run.base_env, run.target_env, run.result,
    base_path=run.base_path,
    target_path=run.target_path,
)

print("Issues found:", diff.has_issues)
```
