"""
Bansoko - Space-themed Sokoban clone created in Python using Pyxel.

Usage:
    python -m bansoko
"""
import pyxel

from game.screens import MainMenuScreen
from gui.screen import ScreenController

CONTROLLER = ScreenController(MainMenuScreen(), pyxel.quit)

if __name__ == "__main__":
    pyxel.init(255, 255, caption="Bansoko", fps=60)
    pyxel.run(CONTROLLER.update, CONTROLLER.draw)
