# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the standalone Bansoko builds.

A spec file rather than a command line so that the Windows and Linux
builds are described in one place and stay reproducible: the --add-data
separator differs between platforms, and the icon only applies on some.

Build with:  pyinstaller bansoko.spec --noconfirm
"""
import importlib.util
import sys
from pathlib import Path

block_cipher = None


def pyxel_runtime_libraries():
    """Collect the shared libraries Pyxel loads by hand at runtime.

    Pyxel's __init__ dlopens SDL2 through ctypes: it tries the system copy
    first and falls back to the one shipped inside the wheel. Neither path is
    visible to PyInstaller's static analysis, so without this the binary ends
    up in one of two bad states. On a machine that happens to have SDL2
    installed, the build silently absorbs the *system* library and inherits
    its glibc requirement, which is how the first Linux build ended up
    demanding a newer glibc than the game needs. On a machine without one, no
    SDL2 is bundled at all and the binary dies on import.

    Collecting the wheel's own copy makes the result independent of whatever
    the build machine has installed.
    """
    spec = importlib.util.find_spec("pyxel")
    if spec is None or not spec.origin:
        raise SystemExit("pyxel must be installed to build the standalone binary")
    libs = Path(spec.origin).parent / "libs"
    if not libs.is_dir():
        # Only Linux relies on this: pyxel/__init__.py guards its ctypes
        # preload with `sys.platform == "linux"`, and the Windows wheel ships
        # no separate libraries at all -- SDL2 is linked into
        # pyxel_binding.pyd, which PyInstaller collects as an ordinary
        # extension module. So a missing directory is normal elsewhere and
        # fatal here --
        # returning [] on Linux would silently produce the exact binary this
        # function exists to prevent, one with no SDL2 that dies on import.
        if sys.platform == "linux":
            raise SystemExit(
                f"pyxel ships no '{libs}'. The SDL2 it loads at runtime cannot "
                "be bundled, so the binary would fail to start. The wheel "
                "layout has changed; update pyxel_runtime_libraries().")
        return []
    # Keep the wheel's layout: Pyxel looks beside its own __file__ for these.
    return [(str(lib), "pyxel/libs") for lib in sorted(libs.iterdir()) if lib.is_file()]

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
    binaries=pyxel_runtime_libraries(),
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
    strip=True,
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
