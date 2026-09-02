"""Shared fixtures for the Bansoko test suite."""
# Requesting a fixture shadows the function that defines it. That is how
# pytest fixtures work, so the check is disabled for this file only.
# pylint: disable=redefined-outer-name
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from bansoko.game.bundle import Bundle, load_bundle

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GAMEDATA_DIR = PROJECT_ROOT / "bansoko" / "gamedata"
RESSRC = PROJECT_ROOT / "resources" / "main.ressrc"


@pytest.fixture(scope="session")
def display() -> str:
    """A usable X display, required by anything that calls pyxel.init().

    Pyxel creates a real OpenGL window even when it is only used to pack
    resources, and its bundled SDL2 has neither the dummy nor the offscreen
    video driver compiled in. Locally this means the test is skipped when
    there is no display; on CI it is a hard failure instead, so that a
    broken Xvfb setup surfaces as a red build rather than a green one that
    quietly tested nothing.
    """
    display_name = os.environ.get("DISPLAY")
    if not display_name:
        if os.environ.get("CI"):
            pytest.fail(
                "No DISPLAY on CI. Resource builder tests need Xvfb; they must not "
                "be silently skipped here.")
        pytest.skip("No DISPLAY available; skipping test that needs pyxel.init()")
    return display_name


@pytest.fixture(scope="session")
def built_resources(display: str, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Run the resource builder from a clean directory and return its output."""
    out_dir = tmp_path_factory.mktemp("gamedata")
    result = subprocess.run(
        [sys.executable, "-m", "resbuilder", str(RESSRC), "--outdir", str(out_dir), "--force"],
        cwd=PROJECT_ROOT,
        env={**os.environ, "DISPLAY": display},
        capture_output=True,
        text=True,
        check=False,
        timeout=600)
    assert result.returncode == 0, (
        f"resbuilder failed ({result.returncode}):\n{result.stdout}\n{result.stderr}")
    return out_dir


@pytest.fixture(scope="session")
def gamedata_dir() -> Path:
    """Directory holding the committed game data."""
    return GAMEDATA_DIR


@pytest.fixture(scope="session")
def bundle(gamedata_dir: Path) -> Bundle:
    """The bundle built from the committed game data."""
    return load_bundle(str(gamedata_dir / "main.meta"))


@pytest.fixture()
def isolated_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point Path.home() at a temporary directory so real profiles are untouched."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    return home


def pytest_report_header(config: pytest.Config) -> str:
    """Make the display situation visible at the top of every test run."""
    del config
    return (f"display: {os.environ.get('DISPLAY') or 'none'} | "
            f"ci: {bool(os.environ.get('CI'))} | "
            f"xvfb-run: {'yes' if shutil.which('xvfb-run') else 'no'}")
