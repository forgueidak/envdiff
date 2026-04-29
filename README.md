# envdiff

Compare `.env` files across environments and report missing or mismatched keys with optional secret masking.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/envdiff.git && cd envdiff && pip install .
```

---

## Usage

```bash
# Compare two .env files
envdiff .env.development .env.production

# Mask secret values in the output
envdiff .env.development .env.production --mask-secrets

# Compare multiple environment files against a base
envdiff .env .env.staging .env.production
```

**Example output:**

```
[MISSING]   DATABASE_URL        present in .env.development, missing in .env.production
[MISMATCH]  LOG_LEVEL           development=debug | production=***
[OK]        APP_NAME            consistent across all environments
```

You can also use `envdiff` as a library:

```python
from envdiff import compare

results = compare(".env.development", ".env.production", mask_secrets=True)
for entry in results:
    print(entry.status, entry.key)
```

---

## Options

| Flag              | Description                          |
|-------------------|--------------------------------------|
| `--mask-secrets`  | Redact values in diff output         |
| `--only-missing`  | Show only missing keys               |
| `--format json`   | Output results as JSON               |

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any significant changes.

---

## License

This project is licensed under the [MIT License](LICENSE).