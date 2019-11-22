import pyxel

from gui.screen import Screen
from .screen_factory import ScreenFactory
from ..level import LevelStatistics


class GameScreen(Screen):
    def __init__(self, screen_factory: ScreenFactory, level: int):
        self.level_stats = LevelStatistics(level)
        self.screen_factory = screen_factory

    def update(self) -> Screen:
        if pyxel.btnp(pyxel.KEY_ESCAPE) or pyxel.btnp(pyxel.GAMEPAD_1_START):
            return self.screen_factory.get_game_paused_screen(self.level_stats.level)
        elif pyxel.btnp(pyxel.KEY_SPACE):
            return self.screen_factory.get_level_completed_screen(self.level_stats)
        return self

    def draw(self) -> None:
        pyxel.cls(0)
        pyxel.text(16, 16, "PLAYING LEVEL " + str(self.level_stats.level), 7)
        pyxel.text(70, 100, "<SPACE> COMPLETE LEVEL " + str(self.level_stats.level), 7)
