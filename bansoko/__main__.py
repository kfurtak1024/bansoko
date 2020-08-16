"""Bansoko - Space-themed Sokoban clone created in Python using Pyxel.

Usage:
    pyxel-bansoko [-h] [--version] [--bundle <name>]

Options:
    -h, --help       Show this screen.
    --version        Show version.
    --bundle <name>  Specify resources bundle name [default: main]
"""
import json
import os
from pathlib import Path

import pyxel
from docopt import docopt

from bansoko import GAME_TITLE, GAME_FRAME_RATE, VERSION
from bansoko.game.context import GameContext
from bansoko.gui.screen import ScreenController

GAMEDATA_PATH = Path(os.path.dirname(os.path.realpath(__file__))).joinpath("gamedata")


def main() -> None:
    """Initializes and starts the game."""
    arguments = docopt(__doc__, version=VERSION)
    bundle_name = arguments["--bundle"]

    with open(GAMEDATA_PATH.joinpath(bundle_name + ".meta").resolve()) as metadata_file:
        pyxel.init(256, 256, caption=GAME_TITLE, fps=GAME_FRAME_RATE, quit_key=pyxel.KEY_F12)
        pyxel.load(str(GAMEDATA_PATH.joinpath(bundle_name + ".pyxres").resolve()))
        game_context = GameContext(json.load(metadata_file))
        controller = ScreenController(game_context.get_main_menu(), pyxel.quit)
        pyxel.run(controller.update, controller.draw)


if __name__ == "__main__":
    main()
