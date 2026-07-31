# ggtmoni

This project reads the local `.env` file, pairs the `GOOGLE_ID_*` values with the
Google API key lines in file order, and shows the next account in rotation with a live countdown.

## What is included

- Web dashboard with live SSE updates
- Native Tkinter GUI
- Terminal countdown monitor
- Shared parser and countdown model
- Regression tests for the shared logic

## Run

Web dashboard:

```bash
python3 app.py
```

By default the web dashboard binds to `0.0.0.0`, so if the machine is on a LAN
you can open it from another device at `http://<machine-ip>:8000`. Set `HOST=127.0.0.1`
or run `python3 app.py --host 127.0.0.1` if you want localhost-only access.

Installed command:

```bash
ggtmoni
```

Native GUI:

```bash
python3 app.py --gui
```

Installed command:

```bash
ggtmoni-gui
```

Terminal monitor:

```bash
python3 realtime_monitor.py
```

Installed command:

```bash
ggtmoni-term
```

Editable install:

```bash
python3 -m pip install -e .
```

If your system Python is externally managed, use a virtual environment first:

```bash
python3 -m venv .venv
.venv/bin/python3 -m pip install -e .
```

## Env file

The app expects a flat `.env` file with ordered pairs like:

```text
GOOGLE_ID_01=someone@example.com
GOOGLE_API_KEY=secret-value
GOOGLE_ID_02=another@example.com
GOOGLE_API_KEY=secret-value
```

The repeated `GOOGLE_API_KEY` name is intentional. The loader uses file order, not variable names, so each identity stays paired with the correct key line.

## Notes

- The web UI reloads when `.env` changes.
- The native GUI reloads when `.env` changes.
- The executable/standalone build looks for `.env` beside the app on Windows.
- Tkinter must be installed globally for `--gui` to open a window.
- Secrets are masked in the UI and API output.

## Windows 11 Standalone

The GUI can be frozen into a standalone Windows 11 executable with PyInstaller.
Use the files in `windows/` from a Windows machine:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[build]"
powershell -ExecutionPolicy Bypass -File windows\build_gui.ps1
```

The build produces `dist\windows\ggtmoni-gui.exe` and
`dist\ggtmoni-windows11-gui.zip`. Place a `.env` file next to the
executable before launching it. Copy `.env.example` and rename it to `.env` if
you need a template.

The same build is available in GitHub Actions as a Windows 11 zip artifact
named `ggtmoni-windows11-gui-zip`.

Tagged releases (`v*`) publish the same zip as a GitHub release asset.
