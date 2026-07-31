# Contributing to ggtmoni

Thanks for improving ggtmoni. Keep changes small, explain the operational
impact, and include tests or documentation for user-visible behavior.

## Local setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[build]"
cp .env.example .env
```

Use placeholder values in `.env` while developing. Never use or commit real
credentials in a test fixture.

## Before opening a pull request

Run:

```bash
make build
git diff --check
```

For UI or CLI changes, also manually exercise the affected interface with a
temporary `.env`. Confirm that credentials remain masked in the UI, terminal
output, HTTP responses, and screenshots.

## Pull requests

- Use a focused branch and describe the user-visible result.
- Link related issues when one exists.
- Document configuration, migration, release, or security changes.
- Include test coverage for parser and countdown behavior.
- Do not include `.env`, API keys, generated `dist/` files, or build output.
- Keep the Windows build and release workflow assumptions documented.

The default branch requires review/checks according to the repository's current
GitHub settings. Maintainers may request changes before merging.

## Commits and releases

Signed commits are preferred and the repository's release process uses signed
version tags:

```bash
git commit -S -m "Describe the change"
git tag -s vX.Y.Z -m "Release vX.Y.Z"
```

Only maintainers publish to PyPI or create GitHub releases. See
[docs/GITHUB.md](docs/GITHUB.md).
