import pyxel

from graphics.menu import Menu, MenuItem
from graphics.screen import Screen
from . import choose_level
from . import game


class MainMenuScreen(Screen):
    def __init__(self):
        self.menu = Menu(
            self,
            [
                MenuItem("Start Game", lambda: game.GameScreen()),
                MenuItem("Choose Level", lambda: choose_level.ChooseLevelScreen()),
                MenuItem("Exit", lambda: None)
            ])

    def update(self):
        return self.menu.update()

    def draw(self):
        pyxel.cls(1)
        pyxel.text(16, 16, "MAIN MENU", 7)
        self.menu.draw()
