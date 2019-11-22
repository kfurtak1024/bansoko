import pyxel

from gui.menu import MenuItem, MenuScreen
from .screen_factory import ScreenFactory


class ChooseLevelScreen(MenuScreen):
    def __init__(self, screen_factory: ScreenFactory):
        super().__init__([
            MenuItem("START LEVEL", lambda: screen_factory.get_game_screen(1)),
            MenuItem("BACK TO MAIN MENU", lambda: None)
        ], 1)

    def draw(self) -> None:
        super().draw()
        pyxel.text(16, 16, "CHOOSE LEVEL", 7)
