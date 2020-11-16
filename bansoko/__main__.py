"""Bansoko - Space-themed Sokoban clone created in Python using Pyxel.

Usage:
    bansoko [-h] [--version] [--bundle <name>]

Options:
    -h, --help       Show this screen.
    --version        Show version.
    --bundle <name>  Specify resources bundle name [default: main]
"""
import os
from dataclasses import dataclass
from pathlib import Path

import pyxel
from docopt import docopt

from bansoko import GAME_FRAME_RATE, __version__, GAME_FRAME_TIME_IN_MS
from bansoko.game.bundle import load_bundle
from bansoko.game.context import GameContext
from bansoko.game.profile import create_or_load_profile
from bansoko.gui.navigator import ScreenNavigator

GAME_TITLE = "Bansoko"


@dataclass(frozen=True)
class FileNames:
    """Container for resource and metadata file names."""
    resource_file: str
    metadata_file: str


def generate_file_names(base_name: str) -> FileNames:
    """Generate resource and metadata file names basing on bundle name.

    :param base_name: name of bundle resource and metadata file names are based on
    :return: instance of FileNames
    """
    base_path = Path(os.path.dirname(os.path.realpath(__file__)))
    gamedata_path = base_path.joinpath("gamedata")
    resource_file = gamedata_path.joinpath(base_name + ".pyxres").resolve()
    metadata_file = gamedata_path.joinpath(base_name + ".meta").resolve()
    return FileNames(str(resource_file), str(metadata_file))


def main() -> None:
    """Main entry point."""
    arguments = docopt(__doc__, version=__version__)
    bundle_name = arguments["--bundle"]
    file_names = generate_file_names(bundle_name)
    pyxel.init(256, 256, caption=GAME_TITLE, fps=GAME_FRAME_RATE, quit_key=pyxel.KEY_F12)
    pyxel.load(file_names.resource_file)
    bundle = load_bundle(file_names.metadata_file)
    player_profile = create_or_load_profile(bundle)
    game_context = GameContext(bundle, player_profile)
    navigator = ScreenNavigator(game_context.get_main_menu(), pyxel.quit, GAME_FRAME_TIME_IN_MS)
    pyxel.run(navigator.update, navigator.draw)


if __name__ == "__main__":
    main()
