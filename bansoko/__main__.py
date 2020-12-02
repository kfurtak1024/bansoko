"""Bansoko - Space-themed Sokoban clone created in Python using Pyxel.

Usage:
    bansoko [-h] [--version] [--bundle <name>]

Options:
    -h, --help       Show this screen.
    --version        Show version.
    --bundle <name>  Specify resources bundle name [default: main]
"""
import logging
import os
from dataclasses import dataclass
from pathlib import Path

import pyxel
from docopt import docopt

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


def main() -> None:
    """Main entry point."""
    arguments = docopt(__doc__, version=__version__)
    bundle_name = arguments["--bundle"]
    filenames = generate_filenames(bundle_name)
    configure_logger(filenames.log_file)
    logging.info("Initializing Pyxel window")
    pyxel.init(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, caption=GAME_TITLE, fps=GAME_FRAME_RATE,
               quit_key=pyxel.KEY_F12)
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
