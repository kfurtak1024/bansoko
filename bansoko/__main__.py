"""Bansoko - Space-themed Sokoban clone created in Python using Pyxel.

Usage:
    pyxel-bansoko [-h] [--version] [--bundle <name>]

Options:
    -h, --help       Show this screen.
    --version        Show version.
    --bundle <name>  Specify resources bundle name [default: main]
"""
import os
from pathlib import Path
from typing import NamedTuple

import pyxel
from docopt import docopt

from bansoko import GAME_TITLE, GAME_FRAME_RATE, VERSION
from bansoko.game.bundle import load_bundle
from bansoko.game.context import GameContext
from bansoko.gui.screen import ScreenController


class FileNames(NamedTuple):
    """Container for resource and metadata file names."""

    resource_file: str
    metadata_file: str


def generate_file_names(bundle_name: str) -> FileNames:
    """
    Generate resource and metadata file names based on bundle name.

    Arguments:
        bundle_name - name of bundle resource and metadata file names are based on

    Returns:
        - instance of FileNames
    """

    base_path = Path(os.path.dirname(os.path.realpath(__file__)))
    gamedata_path = base_path.joinpath("gamedata")
    resource_file = gamedata_path.joinpath(bundle_name + ".pyxres").resolve()
    metadata_file = gamedata_path.joinpath(bundle_name + ".meta").resolve()
    return FileNames(str(resource_file), str(metadata_file))


def main() -> None:
    """Initializes and starts the game."""

    arguments = docopt(__doc__, version=VERSION)
    bundle_name = arguments["--bundle"]
    file_names = generate_file_names(bundle_name)
    pyxel.init(256, 256, caption=GAME_TITLE, fps=GAME_FRAME_RATE, quit_key=pyxel.KEY_F12)
    pyxel.load(file_names.resource_file)
    bundle = load_bundle(file_names.metadata_file)
    game_context = GameContext(bundle)
    controller = ScreenController(game_context.get_main_menu(), pyxel.quit)
    pyxel.run(controller.update, controller.draw)


if __name__ == "__main__":
    main()
