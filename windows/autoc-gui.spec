# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the Windows 11 standalone GUI build.

The executable is windowed, one-file, and expects a .env file next to the EXE.
"""

from pathlib import Path

block_cipher = None
# PyInstaller executes spec files with exec and does not guarantee that
# __file__ exists. build_gui.ps1 sets the working directory to the
# repository root before invoking PyInstaller, so resolve the source files
# from the current directory instead.
project_root = Path.cwd().resolve()

a = Analysis(
    [str(project_root / "gui.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=["tkinter", "tkinter.ttk"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="autoc-gui",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
