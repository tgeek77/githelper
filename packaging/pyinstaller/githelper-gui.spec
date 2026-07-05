# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the githelper GUI."""

from pathlib import Path

block_cipher = None
root = Path(SPECPATH).resolve().parent.parent

hidden = [
    "githelper",
    "githelper.bare",
    "githelper.config",
    "githelper.errors",
    "githelper.heatmap",
    "githelper.info",
    "githelper.remote",
    "githelper.ssh",
]

a = Analysis(
    [str(root / "gui" / "githelper-gui.py")],
    pathex=[str(root)],
    binaries=[],
    datas=[],
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="githelper-gui",
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
