import pyxel

from . import game
from graphics.menu import Menu, MenuItem
from graphics.screen import Screen


class ChooseLevelScreen(Screen):
    def __init__(self):
        self.menu = Menu(
            self,
            [
                MenuItem("Start Level", lambda: game.GameScreen()),
                MenuItem("Back To Main Menu", lambda: None)
            ])

    def update(self):
        return self.menu.update()

    def draw(self):
        pyxel.cls(1)
        pyxel.text(16, 16, "CHOOSE LEVEL", 7)
        self.menu.draw()
