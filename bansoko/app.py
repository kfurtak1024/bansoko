import pyxel

from bansoko.graphics.screen import ScreenController
from game.screens import MainMenuScreen


class App:
    def __init__(self):
        self.controller = ScreenController(MainMenuScreen(), self.__exit_callback)

    def run(self):
        pyxel.init(255, 255, caption="Bansoko", fps=60)
        pyxel.run(self.controller.update, self.controller.draw)

    @staticmethod
    def __exit_callback():
        pyxel.quit()
