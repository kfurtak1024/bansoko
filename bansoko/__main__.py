"""
Bansoko - Space-themed Sokoban clone created in Python using Pyxel.

Usage:
    python -m bansoko
"""
import pyxel

from .game.context import GameContext
from .gui.screen import ScreenController

GAME_TITLE = "Bansoko"
GAME_FRAME_RATE = 30
GAME_RESOURCE_FILE = "gamedata/main.pyxres"

if __name__ == "__main__":
    pyxel.init(256, 256, caption=GAME_TITLE, fps=GAME_FRAME_RATE, quit_key=pyxel.KEY_F12)
    pyxel.load(GAME_RESOURCE_FILE)
    GAME_CONTEXT = GameContext()
    CONTROLLER = ScreenController(GAME_CONTEXT.get_main_menu(), pyxel.quit)
    pyxel.run(CONTROLLER.update, CONTROLLER.draw)
