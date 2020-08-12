"""Bansoko - Space-themed Sokoban clone created in Python using Pyxel.

Usage:
    pyxel-bansoko [-h] [--version] [--bundle <name>]

Options:
    -h, --help       Show this screen.
    --version        Show version.
    --bundle <name>  Specify resources bundle name [default: main]
"""

import pyxel
from docopt import docopt

import game
from bansoko import GAME_TITLE, GAME_FRAME_RATE, VERSION
from bansoko.game.context import GameContext
from bansoko.gui.screen import ScreenController


def main() -> None:
    """Initializes and starts the game."""
    arguments = docopt(__doc__, version=VERSION)
    pyxel.init(256, 256, caption=GAME_TITLE, fps=GAME_FRAME_RATE, quit_key=pyxel.KEY_F12)
    game.load_bundle(arguments["--bundle"])
    game_context = GameContext()
    controller = ScreenController(game_context.get_main_menu(), pyxel.quit)
    pyxel.run(controller.update, controller.draw)


if __name__ == "__main__":
    main()
