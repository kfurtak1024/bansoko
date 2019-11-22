import pyxel

from gui.menu import MenuItem, MenuScreen
from .screen_factory import ScreenFactory


class GamePausedScreen(MenuScreen):
    def __init__(self, screen_factory: ScreenFactory, level: int):
        super().__init__([
            MenuItem("RESUME GAME", lambda: None),
            MenuItem("RESTART LEVEL", lambda: screen_factory.get_game_screen(level)),
            MenuItem("BACK TO MAIN MENU", lambda: screen_factory.get_main_menu())
        ], 1)

    def draw(self) -> None:
        super().draw()
        pyxel.text(16, 16, "GAME PAUSED", 7)
