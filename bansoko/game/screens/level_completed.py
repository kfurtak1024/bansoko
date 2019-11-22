import pyxel

from gui.menu import MenuItem, MenuScreen
from .screen_factory import ScreenFactory
from ..level import LevelStatistics


class LevelCompletedScreen(MenuScreen):
    def __init__(self, screen_factory: ScreenFactory, level_stats: LevelStatistics):
        super().__init__([
            MenuItem("PLAY NEXT LEVEL", lambda: screen_factory.get_game_screen(level_stats.level + 1)),
            MenuItem("RESTART LEVEL", lambda: screen_factory.get_game_screen(level_stats.level)),
            MenuItem("BACK TO MAIN MENU", lambda: screen_factory.get_main_menu())
        ], 1)
        self.level_stats = level_stats

    def draw(self) -> None:
        super().draw()
        pyxel.text(16, 16, "LEVEL " + str(self.level_stats.level) + " COMPLETED", 7)
