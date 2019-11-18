import pyxel

from graphics.menu import Menu, MenuItem
from graphics.screen import Screen
from . import game
from . import main_menu


class LevelCompletedScreen(Screen):
    def __init__(self):
        self.menu = Menu(
            self,
            [
                MenuItem("Play next level", lambda: game.GameScreen()),
                MenuItem("Back To Main Menu", lambda: main_menu.MainMenuScreen())
            ])

    def update(self):
        return self.menu.update()

    def draw(self):
        pyxel.cls(1)
        pyxel.text(16, 16, "LEVEL COMPLETE", 7)
        self.menu.draw()
