import pyxel

from gui.menu import Menu, MenuItem
from gui.screen import Screen
from .screen_factory import ScreenFactory


class GamePausedScreen(Screen):
    def __init__(self, screen_factory: ScreenFactory, level: int):
        self.menu = Menu(
            self,
            [
                MenuItem("RESUME GAME", lambda: None),
                MenuItem("RESTART LEVEL", lambda: screen_factory.get_game_screen(level)),
                MenuItem("BACK TO MAIN MENU", lambda: screen_factory.get_main_menu())
            ])

    def update(self) -> Screen:
        return self.menu.update()

    def draw(self) -> None:
        pyxel.cls(1)
        pyxel.text(16, 16, "GAME PAUSED", 7)
        self.menu.draw()
