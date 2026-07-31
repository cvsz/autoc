# ggtmoni Windows 11 Standalone GUI Build

This folder contains the PyInstaller packaging for the realtime monitor GUI.

Build:

```powershell
powershell -ExecutionPolicy Bypass -File windows\build_gui.ps1
```

Output:

- `dist\windows\ggtmoni-gui.exe`
- `dist\windows\.env.example`
- `dist\ggtmoni-windows11-gui.zip`

Runtime:

- Place a `.env` file beside the EXE.
- The GUI reads token status, active identity, next identity, and countdown
  from the `.env` file beside the executable.
- Tagged releases (`v*`) publish `dist\ggtmoni-windows11-gui.zip` as a
  GitHub release asset.
