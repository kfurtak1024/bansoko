import pyxel

from game.level_stats import LevelStats
from gui.menu import Menu, MenuItem
from gui.screen import Screen
from . import game_paused
from . import level_completed


class GameScreen(Screen):
    def __init__(self, level: int):
        self.level_stats = LevelStats(level)
        self.menu = Menu(
            self,
            [
                MenuItem(
                    "[DEV] Pause Menu",
                    lambda: game_paused.GamePausedScreen(level)),
                MenuItem(
                    "[DEV] Complete Level",
                    lambda: level_completed.LevelCompletedScreen(self.level_stats))
            ])

    def update(self) -> Screen:
        return self.menu.update()

    def draw(self) -> None:
        pyxel.cls(1)
        pyxel.text(16, 16, "PLAYING LEVEL " + str(self.level_stats.level), 7)
        self.menu.draw()
