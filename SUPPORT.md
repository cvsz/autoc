# Support

## Before asking for help

Check the [usage guide](docs/USAGE.md), [operations guide](docs/OPERATIONS.md),
and recent [GitHub Actions runs](https://github.com/cvsz/ggtmoni/actions).
Reproduce with placeholder credentials and collect the command, Python version,
operating system, and sanitized error message.

Never attach `.env`, API keys, full environment dumps, or screenshots that
contain credentials.

## Where to ask

- Use a GitHub issue for a reproducible bug or a clearly scoped feature.
- Use a private security report for suspected vulnerabilities or exposed keys;
  see [SECURITY.md](SECURITY.md).
- Use the GitHub repository discussions/contact channels for operational
  questions that do not fit an issue.

## Useful diagnostics

```bash
python3 --version
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 app.py --env /path/to/synthetic/.env --host 127.0.0.1 --port 8000
```

Include the relevant output after removing identities, tokens, file paths, and
other sensitive values.
