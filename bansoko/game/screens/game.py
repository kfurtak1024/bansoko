import pyxel

from gui.menu import Menu, MenuItem
from gui.screen import Screen
from .screen_factory import ScreenFactory
from ..level import LevelStatistics


class GameScreen(Screen):
    def __init__(self, screen_factory: ScreenFactory, level: int):
        self.level_stats = LevelStatistics(level)
        self.menu = Menu(
            self,
            [
                MenuItem(
                    "[DEV] PAUSE MENU",
                    lambda: screen_factory.get_game_paused_screen(level)),
                MenuItem(
                    "[DEV] COMPLETE LEVEL",
                    lambda: screen_factory.get_level_completed_screen(self.level_stats))
            ])

    def update(self) -> Screen:
        return self.menu.update()

    def draw(self) -> None:
        pyxel.cls(1)
        pyxel.text(16, 16, "PLAYING LEVEL " + str(self.level_stats.level), 7)
        self.menu.draw()
