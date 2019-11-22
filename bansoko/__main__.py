"""
Bansoko - Space-themed Sokoban clone created in Python using Pyxel.

Usage:
    python -m bansoko
"""
import pyxel

from .game.game_context import GameContext
from .gui.screen import ScreenController

GAME_CONTEXT = GameContext()
CONTROLLER = ScreenController(GAME_CONTEXT.get_main_menu(), pyxel.quit)

if __name__ == "__main__":
    pyxel.init(255, 255, caption="Bansoko", fps=30)
    pyxel.run(CONTROLLER.update, CONTROLLER.draw)
