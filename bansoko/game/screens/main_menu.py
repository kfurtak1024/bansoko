import pyxel

from gui.menu import MenuItem, MenuScreen
from .screen_factory import ScreenFactory


class MainMenuScreen(MenuScreen):
    def __init__(self, screen_factory: ScreenFactory):
        super().__init__([
            MenuItem("START GAME", lambda: screen_factory.get_game_screen(1)),
            MenuItem("CHOOSE LEVEL", lambda: screen_factory.get_choose_level_screen()),
            MenuItem("EXIT", lambda: None)
        ], 1)

    def draw(self) -> None:
        super().draw()
        pyxel.text(16, 16, "MAIN MENU", 7)
