import pyxel

from . import main_menu
from graphics.menu import Menu, MenuItem
from graphics.screen import Screen


class GamePausedScreen(Screen):
    def __init__(self):
        self.menu = Menu(
            self,
            [
                MenuItem("Resume Game", lambda: None),
                MenuItem("Restart Level", lambda: None),
                MenuItem("Back To Main Menu", lambda: main_menu.MainMenuScreen())
            ])

    def update(self):
        return self.menu.update()

    def draw(self):
        pyxel.cls(1)
        pyxel.text(16, 16, "GAME PAUSED", 7)
        self.menu.draw()
