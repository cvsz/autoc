# Usage guide

## Configuration file

The loader reads a flat dotenv-style file. It ignores blank lines, comments,
and lines without `=`. A `GOOGLE_ID_*` value is paired with the next key whose
name starts with `GOOGLE_API_KEY`.

```dotenv
# The key name can repeat; order is significant.
GOOGLE_ID_01=first@example.com
GOOGLE_API_KEY=replace-me
GOOGLE_ID_02=second@example.com
GOOGLE_API_KEY=replace-me
```

The loader rejects a dangling identity and an empty configuration. It does not
interpret shell expansion or validate credentials with Google. Keep the file
private and use `chmod 600 .env` on Unix-like systems.

## Web options

```text
app.py [--env PATH] [--interval SECONDS] [--host HOST] [--port PORT] [--gui]
```

Defaults:

| Option | Default | Environment fallback |
| --- | --- | --- |
| `--env` | current directory `.env` (or beside a frozen executable) | none |
| `--interval` | `60` | `MONITOR_INTERVAL_SECONDS` |
| `--host` | `0.0.0.0` | `HOST` |
| `--port` | `8000` | `PORT` |

Use `--host 127.0.0.1` for a local-only dashboard. If the requested port is
busy, the server tries the next available port for up to 50 ports.

## Terminal options

```text
realtime_monitor.py [--env PATH] [--interval SECONDS] [--once]
```

`--once` prints a single masked snapshot and exits. A positive interval is
required.

## HTTP behavior

The dashboard serves:

- `/`: embedded HTML with the initial snapshot;
- `/api/state`: a JSON snapshot with masked display values; and
- `/events`: an SSE stream that emits a snapshot every second; and
- `/healthz`: a small `{"status":"ok","slot_count":N}` health response.

There is no write endpoint. A browser reconnects to `/events` after a network
failure. The server sets `Cache-Control: no-store` on JSON and HTML responses.

The interface also provides a light/dark theme toggle (remembered in browser
storage), identity filtering, a live/offline connection badge, and keyboard
shortcuts: `R` refreshes `/api/state`, while `T` toggles the theme. The GUI
offers the same identity filter plus refresh and timer reset controls.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `missing env file` | Pass the correct `--env` path or create `.env`. |
| `no Google slots found` | Add at least one complete identity/key pair. |
| `without a matching GOOGLE_API_KEY` | Put the key line immediately after its identity. |
| GUI falls back to web | Install/enable Tkinter and run with a graphical session. |
| Browser cannot connect | Check the printed host/port and local firewall. |
| Remote access is unsafe | Bind locally or add an authenticated TLS proxy. |
