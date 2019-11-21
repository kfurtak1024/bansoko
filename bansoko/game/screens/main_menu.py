import pyxel

from gui.menu import Menu, MenuItem
from gui.screen import Screen
from .screen_factory import ScreenFactory


class MainMenuScreen(Screen):
    def __init__(self, screen_factory: ScreenFactory):
        self.menu = Menu(
            self,
            [
                MenuItem("Start Game", lambda: screen_factory.get_game_screen(1)),
                MenuItem("Choose Level", lambda: screen_factory.get_choose_level_screen()),
                MenuItem("Exit", lambda: None)
            ])

    def update(self) -> Screen:
        return self.menu.update()

    def draw(self) -> None:
        pyxel.cls(1)
        pyxel.text(16, 16, "MAIN MENU", 7)
        self.menu.draw()
