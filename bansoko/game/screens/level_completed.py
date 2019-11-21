import pyxel

from gui.menu import Menu, MenuItem
from gui.screen import Screen
from .screen_factory import ScreenFactory
from ..level import LevelStatistics


class LevelCompletedScreen(Screen):
    def __init__(self, screen_factory: ScreenFactory, level_stats: LevelStatistics):
        self.level_stats = level_stats
        self.menu = Menu(
            self,
            [
                MenuItem("PLAY NEXT LEVEL", lambda: screen_factory.get_game_screen(level_stats.level + 1)),
                MenuItem("RESTART LEVEL", lambda: screen_factory.get_game_screen(level_stats.level)),
                MenuItem("BACK TO MAIN MENU", lambda: screen_factory.get_main_menu())
            ])

    def update(self) -> Screen:
        return self.menu.update()

    def draw(self) -> None:
        pyxel.cls(1)
        pyxel.text(16, 16, "LEVEL " + str(self.level_stats.level) + " COMPLETED", 7)
        self.menu.draw()
