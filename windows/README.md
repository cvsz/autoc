# autoc Windows 11 standalone GUI build

This folder contains the PyInstaller packaging for the realtime monitor GUI.

The build is intended for Windows 11 and produces a one-file, windowed
executable. It does not embed credentials: `.env` is copied only as a
placeholder template and must be replaced or edited locally after extraction.

Build:

```powershell
powershell -ExecutionPolicy Bypass -File windows\build_gui.ps1
```

Output:

- `dist\windows\autoc-gui.exe`
- `dist\windows\.env.example`
- `dist\autoc-windows11-gui.zip`

Runtime:

- Place a `.env` file beside the EXE.
- The GUI reads token status, active identity, next identity, and countdown
  from the `.env` file beside the executable.
- Keep the extracted directory private because the application needs to read
  the raw local `.env` file.
- Tagged releases (`v*`) publish `dist\autoc-windows11-gui.zip` as a
  GitHub release asset.

The automated workflow also checks that the EXE, `.env.example`, and zip are
present and runs `autoc-gui.exe --help` as a smoke test. See
[the main usage guide](../docs/USAGE.md) and [release operations](../docs/OPERATIONS.md)
for configuration and distribution guidance.
