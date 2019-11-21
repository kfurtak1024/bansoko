import pyxel

from gui.menu import Menu, MenuItem
from gui.screen import Screen
from . import game


class ChooseLevelScreen(Screen):
    def __init__(self):
        self.menu = Menu(
            self,
            [
                MenuItem("Start Level", lambda: game.GameScreen(1)),
                MenuItem("Back To Main Menu", lambda: None)
            ])

    def update(self) -> Screen:
        return self.menu.update()

    def draw(self) -> None:
        pyxel.cls(1)
        pyxel.text(16, 16, "CHOOSE LEVEL", 7)
        self.menu.draw()
