# GitHub configuration

Repository: <https://github.com/cvsz/autoc>

## Actions workflows

| Workflow | Trigger | Result |
| --- | --- | --- |
| `CI` | push and pull request to `main` | Python tests and package validation |
| `Windows GUI Build` | relevant source changes or manual dispatch | Windows executable artifact and smoke test |
| `Windows GUI Release` | `v*` tag or manual dispatch | GitHub release with Windows zip |
| `Publish Python Package` | `v*` tag or manual dispatch | PyPI distribution upload |

All release/build jobs use the `production` environment. The shared variables
are `PYTHON_VERSION` and `RELEASE_ASSET_NAME`. The PyPI workflow uses the
environment secret `PYPI_API_KEY`; its value must never be committed or
printed.

## Publishing a release

```bash
make build
git tag -s vX.Y.Z -m "Release vX.Y.Z"
git push origin main vX.Y.Z
```

The tag must point at the reviewed source commit. Inspect Actions and the
release page after pushing. A package version already on PyPI cannot be
overwritten; increment the version for a new upload.

## Maintainer settings

Keep these repository settings current:

- default branch: `main`;
- Actions enabled with least-privilege workflow permissions;
- `production` environment approval/secrets appropriate for publishing;
- branch protection and required CI checks where the account plan supports it;
- issue templates, pull-request template, security policy, and code of conduct;
- repository description and topics that match the project.

Never store Google credentials in repository variables, issues, artifacts, or
workflow logs. Environment secrets are exposed only to jobs that explicitly
reference the environment.

## Troubleshooting Actions

1. Open the failed run and identify the first failing step.
2. Confirm the workflow has the expected environment and variable names.
3. Check that the tag version matches `pyproject.toml`.
4. For PyPI authentication failures, rotate the API token and update only the
   `production` environment secret.
5. Re-run after correcting configuration; do not weaken secret masking.
