"""Bansoko - Space-themed Sokoban clone created in Python using Pyxel.

Usage:
    pyxel-bansoko [-h] [--version] [--bundle <name>]

Options:
    -h, --help       Show this screen.
    --version        Show version.
    --bundle <name>  Specify resources bundle name [default: main]
"""
import pyxel

from bansoko.game.context import GameContext
from bansoko.gui.screen import ScreenController

GAME_TITLE = "Bansoko"
GAME_FRAME_RATE = 30
GAME_RESOURCE_FILE = "gamedata/main.pyxres"


def main() -> None:
    """Initializes and starts the game."""
    pyxel.init(256, 256, caption=GAME_TITLE, fps=GAME_FRAME_RATE, quit_key=pyxel.KEY_F12)
    pyxel.load(GAME_RESOURCE_FILE)
    game_context = GameContext()
    controller = ScreenController(game_context.get_main_menu(), pyxel.quit)
    pyxel.run(controller.update, controller.draw)


if __name__ == "__main__":
    main()
