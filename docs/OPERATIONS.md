# Operations and releases

## Local service operation

Run the web dashboard from a virtual environment:

```bash
cd /path/to/ggtmoni
.venv/bin/python app.py --env /secure/path/.env --host 127.0.0.1 --port 8000
```

For remote users, place an authenticated TLS reverse proxy in front of the
process. The application itself has no authentication, authorization, TLS,
health endpoint, or persistent database.

Before changing `.env`, prepare the complete replacement file and move it into
place atomically where practical. The running process notices the mtime change
and creates a fresh countdown model.

## Windows executable

Build and inspect the zip on Windows before distributing it. The executable
expects `.env` in its own directory. Do not put real credentials into the zip
or GitHub artifact.

## Release checklist

1. Update `version` in `pyproject.toml`.
2. Update `CHANGELOG.md` and relevant user documentation.
3. Run `make build` and `git diff --check`.
4. Create and push a signed `vX.Y.Z` tag.
5. Confirm Windows build, GitHub release, and PyPI publication succeed.
6. Verify the package metadata and release asset from their public pages.

The tag starts the Windows release and PyPI workflows. A manual package run
can select an existing release tag. Re-running a publish for an already
uploaded version will fail unless the package upload is configured to skip
existing files; treat that as an expected immutable-version safeguard.

## Rollback

Published PyPI versions and GitHub release assets are immutable in normal
operation. Roll back consumers by pinning a known-good version and revoke or
rotate credentials if a release contained sensitive data. Fix the source and
publish a new version rather than reusing a version number.
