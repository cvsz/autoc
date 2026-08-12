<div align="center">
  <h1>🚀 autoc</h1>
  <h3>Enterprise-Grade Realtime Monitoring & Conversational Commerce OS</h3>
  <p>v1.0.0-GOLD-MASTER (Fully Completed)</p>
</div>

**autoc** is the ultimate backend rotation engine combined with a massive suite of features: Helpdesk, Automations, AI Agents, Analytics, and Broadcasts. All natively baked into a single lightweight Python ecosystem with a SQLite database.

> Security: this tool is a local operations monitor, not an API-key vault. Do
> not commit `.env`, expose the dashboard to an untrusted network, or paste
> real credentials into an issue, log, screenshot, or support request. See
> [SECURITY.md](SECURITY.md).

## Requirements

- Python 3.11 or newer
- A local `.env` file containing at least one complete identity/key pair
- Tkinter only when using the desktop GUI

No runtime third-party package is required for the web or terminal interfaces.
The optional `build` extra installs PyInstaller for the Windows executable.

## Quick start

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
cp .env.example .env
# Edit .env and replace every placeholder with a real value.
./.venv/bin/python app.py --host 127.0.0.1
```

Open <http://127.0.0.1:8000>. The server prints the actual port if port 8000
is already in use.

The installed console commands are:

```bash
autoc                 # web dashboard
autoc-gui             # Tkinter GUI
autoc-term --once     # one terminal snapshot
```

See [docs/USAGE.md](docs/USAGE.md) for all options and examples.

## Configuration

Copy `.env.example` to `.env`. Pair each `GOOGLE_ID_*` line with the next
`GOOGLE_API_KEY*` line. The key name may repeat intentionally; pairing is based
on file order.

```dotenv
GOOGLE_ID_01=first@example.com
GOOGLE_API_KEY=replace-me
GOOGLE_ID_02=second@example.com
GOOGLE_API_KEY=replace-me
```

Important rules:

- Keep each identity immediately before its matching key.
- At least one complete pair is required.
- A `GOOGLE_ID_*` without a following key is an error.
- `MONITOR_INTERVAL_SECONDS` controls the default web-dashboard interval.
- `HOST` and `PORT` provide web-dashboard defaults; CLI flags override them.
- The desktop executable looks for `.env` beside the executable.

The parser does not perform Google API calls or validate the credentials with
Google. It only loads, pairs, rotates, and masks the configured values.

## Interfaces

### Web dashboard

```bash
python3 app.py --env .env --interval 60 --host 127.0.0.1 --port 8000
```

Routes:

| Route | Purpose |
| --- | --- |
| `/` | Dashboard HTML and initial state |
| `/api/state` | One JSON state snapshot |
| `/events` | One-way live state stream using SSE |
| `/healthz` | Lightweight JSON health check for local process monitors |

The HTTP server has no authentication or TLS. Bind to `127.0.0.1` for local
use, or put it behind an authenticated reverse proxy before using a wider
network binding.

### Native GUI

```bash
python3 app.py --gui --env .env --interval 60
# or
python3 gui.py --env .env --interval 60
```

The GUI supports refresh, timer reset, live file reload, and a masked slot
table with filtering. If Tkinter is unavailable, `app.py --gui` falls back to
the web dashboard and reports the reason on stderr.

The web dashboard adds a live connection indicator, light/dark theme toggle,
slot filtering, keyboard shortcuts (`R` refresh and `T` theme), and a `/healthz`
endpoint for process monitors. Each configured key is shown only as a masked
value plus length and a short non-reversible fingerprint.

`autoc` reports local rotation state (`active`, `next`, or `queued`). It does
not call Google APIs or collect provider quota/usage telemetry, so no frontend
can claim live Google usage from this application alone.

### Terminal monitor

```bash
python3 realtime_monitor.py --env .env --interval 60
python3 realtime_monitor.py --env .env --once
```

Press `Ctrl+C` to stop a continuously running terminal monitor.

## Development

```bash
make build
```

This creates or uses `.venv`, installs the project, compiles the modules, and
runs the standard-library test suite. To run only tests:

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```

The project intentionally keeps the runtime small: `monitor_core.py` owns
parsing, masking, countdown state, and reload behavior; the three frontends
render that shared state. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Windows 11 standalone build

From Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[build]"
powershell -ExecutionPolicy Bypass -File windows\build_gui.ps1
```

The build creates:

- `dist\windows\autoc-gui.exe`
- `dist\windows\.env.example`
- `dist\autoc-windows11-gui.zip`

Put a private `.env` beside the executable before starting it. Detailed
packaging notes are in [windows/README.md](windows/README.md).

## Releases and packages

The GitHub Actions workflows provide:

- `Windows GUI Build`: builds and smoke-tests the standalone executable.
- `Windows GUI Release`: publishes the Windows zip for a `v*` tag.
- `Publish Python Package`: builds and uploads the package to PyPI.

To create a release locally, update the version in `pyproject.toml`, run the
tests, create a signed tag, and push it:

```bash
make build
git tag -s vX.Y.Z -m "Release vX.Y.Z"
git push origin main vX.Y.Z
```

The package workflow uses the `production` GitHub environment and its
`PYPI_API_KEY` secret. Never put that value in the repository. See
[docs/GITHUB.md](docs/GITHUB.md) for workflow, environment, and release
operations.

## Web application

The repository also contains the web application under `autoc-clone/` while the
legacy folder name is being retired. Product branding and package identity are
being migrated from autoc to `autoc` as part of the repository-wide rebrand.

## Documentation map

- [Usage guide](docs/USAGE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Operations and releases](docs/OPERATIONS.md)
- [GitHub configuration](docs/GITHUB.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Support](SUPPORT.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Changelog](CHANGELOG.md)
- [Design notes](realtime-monitor-countdown-design.md)

## License

This repository currently has no declared open-source license. Until a license
is added by the copyright holder, treat the source as proprietary and ask the
maintainer before redistributing or incorporating it into another project.
