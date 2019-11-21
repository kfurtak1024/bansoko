import pyxel

from game.level_stats import LevelStats
from gui.menu import Menu, MenuItem
from gui.screen import Screen
from . import game
from . import main_menu


class LevelCompletedScreen(Screen):
    def __init__(self, level_stats: LevelStats):
        self.level_stats = level_stats
        self.menu = Menu(
            self,
            [
                MenuItem("Continue To Next Level", lambda: game.GameScreen(level_stats.level + 1)),
                MenuItem("Restart Level", lambda: game.GameScreen(level_stats.level)),
                MenuItem("Back To Main Menu", lambda: main_menu.MainMenuScreen())
            ])

    def update(self) -> Screen:
        return self.menu.update()

    def draw(self) -> None:
        pyxel.cls(1)
        pyxel.text(16, 16, "LEVEL " + str(self.level_stats.level) + " COMPLETED", 7)
        self.menu.draw()
