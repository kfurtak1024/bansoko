# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the standalone Bansoko builds.

A spec file rather than a command line so that the Windows and Linux
builds are described in one place and stay reproducible: the --add-data
separator differs between platforms, and the icon only applies on some.

Build with:  pyinstaller bansoko.spec --noconfirm
"""
import sys
from pathlib import Path

block_cipher = None

# The game locates its resources relative to bansoko/__main__.py. PyInstaller
# places the entry script at the root of the bundle rather than inside the
# package, so __file__ resolves to _MEIPASS and the resources have to sit at
# the top level, not under bansoko/. Getting this wrong produces a binary that
# builds cleanly and then fails at startup with "Unable to find Pyxel resource
# file", so tests/test_frozen_build.py checks that a built binary actually starts.
datas = [("bansoko/gamedata", "gamedata")]

icon = "resources/bansoko.ico" if Path("resources/bansoko.ico").is_file() else None

a = Analysis(
    ["bansoko/__main__.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pylint", "mypy", "pytest", "PyInstaller", "setuptools"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="bansoko",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    # The game opens its own window; a console would sit behind it.
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)
