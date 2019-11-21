import pyxel

from gui.menu import Menu, MenuItem
from gui.screen import Screen
from . import game
from . import main_menu


class GamePausedScreen(Screen):
    def __init__(self, level: int):
        self.menu = Menu(
            self,
            [
                MenuItem("Resume Game", lambda: None),
                MenuItem("Restart Level", lambda: game.GameScreen(level)),
                MenuItem("Back To Main Menu", lambda: main_menu.MainMenuScreen())
            ])

    def update(self) -> Screen:
        return self.menu.update()

    def draw(self) -> None:
        pyxel.cls(1)
        pyxel.text(16, 16, "GAME PAUSED", 7)
        self.menu.draw()
