import pyxel

from gui.menu import Menu, MenuItem
from gui.screen import Screen
from .screen_factory import ScreenFactory


class GamePausedScreen(Screen):
    def __init__(self, screen_factory: ScreenFactory, level: int):
        self.menu = Menu(
            self,
            [
                MenuItem("Resume Game", None),
                MenuItem("Restart Level", lambda: screen_factory.get_game_screen(level)),
                MenuItem("Back To Main Menu", lambda: screen_factory.get_main_menu())
            ])

    def update(self) -> Screen:
        return self.menu.update()

    def draw(self) -> None:
        pyxel.cls(1)
        pyxel.text(16, 16, "GAME PAUSED", 7)
        self.menu.draw()
