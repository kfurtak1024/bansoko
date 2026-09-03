"""Bansoko - Space-themed Sokoban clone created in Python using Pyxel."""
import argparse
import ctypes
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import pyxel

from bansoko import GAME_FRAME_RATE, __version__, GAME_FRAME_TIME_IN_MS
from bansoko.game import GameError
from bansoko.game.bundle import load_bundle, Bundle
from bansoko.game.context import GameContext
from bansoko.game.profile import create_or_load_profile, GAME_PROFILE_LOCATION, \
    GAME_PROFILE_FILENAME, GAME_LOG_FILENAME
from bansoko.game.screens.error import show_error_message
from bansoko.graphics import SCREEN_WIDTH, SCREEN_HEIGHT
from bansoko.gui.navigator import ScreenNavigator

GAME_TITLE = "Bansoko"


@dataclass(frozen=True)
class FileNames:
    """Container for resource and metadata file names."""
    resource_file: str
    metadata_file: str
    profile_file_path: Path
    log_file: str


def generate_filenames(base_name: str) -> FileNames:
    """Generate resource and metadata file names basing on bundle name.

    :param base_name: name of bundle resource and metadata file names are based on
    :return: instance of FileNames
    """
    base_path = Path(os.path.dirname(os.path.realpath(__file__)))
    gamedata_path = base_path.joinpath("gamedata")
    resource_file = gamedata_path.joinpath(base_name + ".pyxres").resolve()
    metadata_file = gamedata_path.joinpath(base_name + ".meta").resolve()
    profile_dir = Path.home().joinpath(GAME_PROFILE_LOCATION)
    os.makedirs(profile_dir, exist_ok=True)
    profile_file_path = profile_dir.joinpath(GAME_PROFILE_FILENAME)
    log_file = profile_dir.joinpath(GAME_LOG_FILENAME)
    return FileNames(str(resource_file), str(metadata_file), profile_file_path, str(log_file))


def configure_logger(log_filename: str) -> None:
    """Sets up a logger for Bansoko."""
    logging.basicConfig(filename=log_filename, filemode="w",
                        format="%(levelname)s%(message)s",
                        level=logging.INFO)
    logging.addLevelName(logging.ERROR, "** ERROR: ")
    logging.addLevelName(logging.WARN, "WARN: ")
    logging.addLevelName(logging.INFO, "")
    logging.info("Starting Bansoko %s", __version__)


def load_game_resources(filenames: FileNames) -> Bundle:
    """Load Pyxel's resource file containing bundle."""
    logging.info("Loading Pyxel resources file '%s'", filenames.resource_file)
    if not os.path.isfile(filenames.resource_file):
        # This is the only way we can pre-check whether pyxel.load() will fail or not
        # In current version of Pyxel it's not possible to react to error or capture the error
        # reason
        raise GameError(f"Unable to find Pyxel resource file '{filenames.resource_file}'")
    pyxel.load(filenames.resource_file)

    logging.info("Loading resources metadata file '%s'", filenames.metadata_file)
    if not os.path.isfile(filenames.metadata_file):
        raise GameError(f"Unable to find resources metadata file '{filenames.metadata_file}'")

    return load_bundle(filenames.metadata_file)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="bansoko",
        description="Bansoko - Space-themed Sokoban clone created in Python using Pyxel.")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--bundle", metavar="<name>", default="main",
                        help="Specify resources bundle name (default: %(default)s)")
    return parser.parse_args()


# Fragments of the messages Pyxel's Rust layer produces when it cannot get a
# usable OpenGL context. Matched case-insensitively against the panic text.
#
# Every marker has to be specific enough that no other failure can contain it:
# a false match tells the player to update their graphics drivers when the real
# problem is somewhere else entirely. "was not loaded" was one such marker, and
# it was also redundant -- the panic it was there for, "called glCreateShader
# but it was not loaded", already matches on "glcreateshader".
GRAPHICS_FAILURE_MARKERS = (
    "no available video device",
    "failed to initialize sdl2",
    "failed to create window",
    "opengl",
    "glcreateshader",
)

GRAPHICS_ERROR_MESSAGE = (
    "Bansoko needs OpenGL, and it could not be initialised on this machine.\n\n"
    "This usually means one of:\n"
    "  - the graphics drivers need updating or are not installed yet,\n"
    "  - the game is running in a virtual machine or a remote desktop\n"
    "    session without 3D acceleration.\n"
)


def is_graphics_failure(message: str) -> bool:
    """Does this failure look like a missing or broken OpenGL setup?

    Pyxel surfaces these as a Rust panic whose only useful content is the
    message, so matching on the text is the only option available.
    """
    lowered = message.lower()
    return any(marker in lowered for marker in GRAPHICS_FAILURE_MARKERS)


def should_use_error_dialog() -> bool:
    """Is a modal dialog the only way to reach whoever launched the game?

    Only one situation qualifies: the frozen, windowed Windows build, which
    has no console and leaves stderr with nowhere to go.

    The sys.frozen check is what makes this safe. An earlier version asked
    Windows for a console window instead, which is wrong under CI: GitHub
    Actions redirects stdio and attaches no console, so the check reported
    "no console", a dialog opened on a headless runner, and the test run hung
    until the job timed out. Running from source -- development, tests, CI --
    can now never open a dialog, whatever the console situation.
    """
    if sys.platform != "win32":
        return False
    if not getattr(sys, "frozen", False):
        return False
    return sys.stderr is None


def show_error_dialog(message: str) -> None:
    """Show a modal error dialog. Windows only, and only without a console."""
    try:
        # windll only exists on Windows, hence the getattr.
        user32 = getattr(ctypes, "windll").user32
        user32.MessageBoxW(None, message, GAME_TITLE, 0x10)  # MB_ICONERROR
    except Exception:  # pylint: disable=broad-except
        # A missing dialog must never replace the original failure.
        logging.exception("Could not display the error dialog")


def report_startup_failure(message: str) -> None:
    """Tell the player why the game will not start."""
    logging.error(message)

    if sys.stderr is not None:
        print(message, file=sys.stderr)

    if should_use_error_dialog():
        show_error_dialog(message)


def initialize_display() -> None:
    """Open the game window, explaining an OpenGL failure in plain language.

    Pyxel raises a PanicException from its Rust layer, which derives from
    BaseException rather than Exception, so it slips past an ordinary
    "except Exception". Anything that does not look like a graphics problem
    is re-raised untouched rather than being hidden behind a friendly note.
    """
    try:
        pyxel.init(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=GAME_TITLE,
                   fps=GAME_FRAME_RATE, quit_key=pyxel.KEY_F12, capture_sec=0)
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as error:
        if not is_graphics_failure(str(error)):
            raise
        logging.exception("Pyxel could not initialise the display")
        report_startup_failure(f"{GRAPHICS_ERROR_MESSAGE}\nTechnical detail: {error}")
        raise SystemExit(1) from error


def main() -> None:
    """Main entry point."""
    bundle_name = parse_args().bundle
    filenames = generate_filenames(bundle_name)
    configure_logger(filenames.log_file)
    logging.info("Initializing Pyxel window")
    initialize_display()
    try:
        bundle = load_game_resources(filenames)
        logging.info("Bundle name: %s", bundle_name)
        logging.info("Bundle SHA1: %s", bundle.sha1.decode())
        player_profile = create_or_load_profile(bundle, filenames.profile_file_path)
        game_context = GameContext(bundle, player_profile)
        navigator = ScreenNavigator(game_context.get_main_menu(), pyxel.quit, GAME_FRAME_TIME_IN_MS)
        logging.info("Game started.")
        pyxel.run(navigator.update, navigator.draw)
    except GameError as error:
        logging.exception(error)
        show_error_message(error.message)


if __name__ == "__main__":
    main()
