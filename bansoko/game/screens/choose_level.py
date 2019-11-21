import pyxel

from gui.menu import Menu, MenuItem
from gui.screen import Screen
from .screen_factory import ScreenFactory


class ChooseLevelScreen(Screen):
    def __init__(self, screen_factory: ScreenFactory):
        self.menu = Menu(
            self,
            [
                MenuItem("Start Level", lambda: screen_factory.get_game_screen(1)),
                MenuItem("Back To Main Menu", lambda: None)
            ])

    def update(self) -> Screen:
        return self.menu.update()

    def draw(self) -> None:
        pyxel.cls(1)
        pyxel.text(16, 16, "CHOOSE LEVEL", 7)
        self.menu.draw()
