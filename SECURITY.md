# Security policy

## Scope

autoc reads Google identity and API-key values from a local `.env` file and
renders a rotating operational view. It does not authenticate users, encrypt
the file, call Google APIs, or provide a secrets-management service.

The HTTP dashboard has no authentication or TLS. Treat a non-local bind as a
network service that must be protected by an authenticated reverse proxy,
firewall, or private network.

## Protecting credentials

- Keep `.env` outside version control and restrict its filesystem permissions.
- Start the dashboard with `--host 127.0.0.1` unless remote access is required.
- Never paste credentials into issues, logs, screenshots, CI output, or chat.
- Rotate a key immediately if it may have been exposed.
- Use a secret manager or GitHub Actions environment secrets for CI-only values.
- Do not use production credentials in tests or local examples.

The application masks API-key values in rendered state. Masking is not a
replacement for access control; anyone who can read the process, `.env`, or an
unprotected dashboard should be treated as trusted.

## Reporting a vulnerability

Do not open a public issue for a suspected credential leak or exploitable
security problem. Contact the repository owner privately through the GitHub
profile or repository security contact. Include a concise description,
affected version/commit, reproduction steps that use synthetic data, and the
impact. Do not include live secrets.

If a secret is involved, rotate or revoke it first, then report the event with
the secret omitted. Maintainers will acknowledge reports, assess impact, and
coordinate a fix or disclosure timeline.
