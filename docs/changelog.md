# Changelog

The `changelog` feature lets you **record** successive diff runs and **review** how your environment drift evolves over time.

## Concepts

| Term | Description |
|---|---|
| `ChangelogEntry` | A single diff snapshot: timestamp, labels, and issue lists |
| `Changelog` | An ordered collection of `ChangelogEntry` objects |

---

## Python API

```python
from envdiff.changelog import record_entry, Changelog, save_changelog, load_changelog
from envdiff.comparator import compare_envs
from envdiff.parser import parse_env_files

envs = parse_env_files([".env.dev", ".env.prod"])
result = compare_envs(envs[0], envs[1])

entry = record_entry(result, base_label="dev", target_label="prod")

cl = Changelog()
cl.add(entry)

save_changelog(cl, Path(".envdiff_changelog.json"))
```

### Loading an existing changelog

```python
cl = load_changelog(Path(".envdiff_changelog.json"))
for entry in cl.entries:
    print(entry.timestamp, entry.total_issues)
```

---

## CLI

### Record a diff

```bash
envdiff changelog record .env.dev .env.prod
```

Optional flags:

| Flag | Default | Description |
|---|---|---|
| `--changelog` | `.envdiff_changelog.json` | Path to the changelog file |
| `--mask-secrets` | off | Mask secret values before recording |

### Show the changelog

```bash
envdiff changelog show
envdiff changelog show --limit 5
```

Optional flags:

| Flag | Default | Description |
|---|---|---|
| `--changelog` | `.envdiff_changelog.json` | Path to the changelog file |
| `--limit` | 0 (all) | Show only the N most recent entries |

---

## Output format

The changelog is stored as a JSON file:

```json
{
  "entries": [
    {
      "timestamp": "2024-06-01T12:00:00+00:00",
      "base": ".env.dev",
      "target": ".env.prod",
      "missing_in_target": ["DB_HOST"],
      "missing_in_base": [],
      "mismatched": ["API_URL"],
      "total_issues": 2
    }
  ]
}
```

---

## Integration tip

Add a `record` step to your CI pipeline after every deployment to build a historical audit trail of environment drift.
