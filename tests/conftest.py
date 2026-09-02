"""Shared fixtures for the Bansoko test suite."""
# Requesting a fixture shadows the function that defines it. That is how
# pytest fixtures work, so the check is disabled for this file only.
# pylint: disable=redefined-outer-name
import functools
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import pyxel

from bansoko.game.bundle import Bundle, load_bundle
from bansoko.game.context import GameContext
from bansoko.game.level import Level
from bansoko.game.profile import create_or_load_profile
from bansoko.graphics import SCREEN_HEIGHT, SCREEN_WIDTH

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GAMEDATA_DIR = PROJECT_ROOT / "bansoko" / "gamedata"
RESSRC = PROJECT_ROOT / "resources" / "main.ressrc"


REQUIRE_GRAPHICS_ENV = "BANSOKO_REQUIRE_GRAPHICS"


@functools.cache
def _probe_graphics() -> str:
    """Try to open a Pyxel window in a subprocess; return "" on success.

    Whether pyxel.init() works cannot be inferred from the platform. A
    Windows CI runner has a window server but no OpenGL driver, so SDL2
    creates the window and then dies on the first shader call. Asking the
    real thing in a throwaway process is the only honest answer, and it is
    cheap because the result is cached for the whole session.
    """
    result = subprocess.run(
        [sys.executable, "-c", "import pyxel; pyxel.init(32, 32)"],
        capture_output=True, text=True, check=False, timeout=120)
    if result.returncode == 0:
        return ""
    return (result.stderr or result.stdout or "no output").strip().splitlines()[-1]


@pytest.fixture(scope="session")
def graphics() -> None:
    """Gate for tests that need pyxel.init(), which needs working OpenGL.

    Pyxel opens a real OpenGL window even when it is only used to pack
    resources, and its bundled SDL2 has neither the dummy nor the offscreen
    video driver compiled in.

    Where graphics are expected to work, set BANSOKO_REQUIRE_GRAPHICS so a
    broken setup fails loudly instead of skipping: a green build that
    quietly tested nothing is worse than a red one. Everywhere else --- a
    headless workstation, or a CI runner with no GL driver --- these tests
    skip with the reason the probe actually reported.
    """
    reason = _probe_graphics()
    if not reason:
        return
    message = f"Pyxel cannot open a window here: {reason}"
    if os.environ.get(REQUIRE_GRAPHICS_ENV):
        pytest.fail(
            f"{message}\n\n{REQUIRE_GRAPHICS_ENV} is set, so these tests are "
            f"required to run here and must not be skipped.")
    pytest.skip(message)


@pytest.fixture(scope="session")
def built_resources(graphics: None, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Run the resource builder from a clean directory and return its output."""
    del graphics  # Depended on for its skip/fail behaviour only.
    out_dir = tmp_path_factory.mktemp("gamedata")
    result = subprocess.run(
        [sys.executable, "-m", "resbuilder", str(RESSRC), "--outdir", str(out_dir), "--force"],
        cwd=PROJECT_ROOT,
        env=os.environ.copy(),
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


@pytest.fixture(scope="session")
def pyxel_runtime(graphics: None, gamedata_dir: Path) -> None:
    """Initialise Pyxel once per session and load the game's resources.

    Level layouts live in the tilemaps inside main.pyxres, so anything that
    builds a Level needs this even though the rules themselves are pure
    Python. Pyxel can only be initialised once in a process, hence session
    scope.
    """
    del graphics  # Depended on for its skip/fail behaviour only.
    pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT)
    pyxel.load(str(gamedata_dir / "main.pyxres"))


@pytest.fixture()
def game_context(pyxel_runtime: None, bundle: Bundle, tmp_path: Path) -> GameContext:
    """A game context backed by a throwaway player profile."""
    del pyxel_runtime  # Ordering dependency: resources must be loaded first.
    profile = create_or_load_profile(bundle, tmp_path / "profile.data")
    return GameContext(bundle, profile)


@pytest.fixture()
def level(pyxel_runtime: None, bundle: Bundle) -> Level:
    """The tutorial level (level 0), freshly started."""
    del pyxel_runtime  # Ordering dependency: resources must be loaded first.
    return Level(bundle.get_level_template(0))


@pytest.fixture()
def frozen_binary() -> Path:
    """Path to a built standalone binary, from BANSOKO_FROZEN_BINARY.

    Set by the release workflow after PyInstaller runs, so the frozen-build
    smoke test costs nothing during an ordinary test run.
    """
    binary = os.environ.get("BANSOKO_FROZEN_BINARY")
    if not binary:
        pytest.skip("BANSOKO_FROZEN_BINARY is not set; no frozen build to check")
    path = Path(binary).resolve()
    assert path.is_file(), f"BANSOKO_FROZEN_BINARY does not exist: {path}"
    return path


def pytest_report_header(config: pytest.Config) -> str:
    """Report the real graphics situation at the top of every test run."""
    del config
    reason = _probe_graphics()
    status = "available" if not reason else f"unavailable ({reason})"
    required = "required" if os.environ.get(REQUIRE_GRAPHICS_ENV) else "optional"
    return (f"pyxel graphics: {status} | {required} | "
            f"display: {os.environ.get('DISPLAY') or 'none'} | "
            f"xvfb-run: {'yes' if shutil.which('xvfb-run') else 'no'}")
