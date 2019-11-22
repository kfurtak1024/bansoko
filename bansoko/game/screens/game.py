"""
Module exposing the main game screen.
"""
import pyxel

from .screen_factory import ScreenFactory
from ..level import LevelStatistics
from ...gui.screen import Screen


class GameScreen(Screen):
    """
    Main game screen.
    Screen allows player to "play" the level. It evaluates end-game conditions
    and switches to Level Completed screen when those are met.
    It is also possible to pause the game by pressing either 'Escape' or 'Start'
    (on a gamepad). That switches to Game Paused screen.

    Arguments:
        screen_factory - used for creation of screens this screen will navigate to
    """

    def __init__(self, screen_factory: ScreenFactory, level: int):
        self.level_stats = LevelStatistics(level)
        self.screen_factory = screen_factory

    def update(self) -> Screen:
        if pyxel.btnp(pyxel.KEY_ESCAPE) or pyxel.btnp(pyxel.GAMEPAD_1_START):
            return self.screen_factory.get_game_paused_screen(self.level_stats.level)
        if pyxel.btnp(pyxel.KEY_SPACE):
            return self.screen_factory.get_level_completed_screen(self.level_stats)
        return self

    def draw(self) -> None:
        pyxel.cls(0)
        pyxel.text(16, 16, "PLAYING LEVEL " + str(self.level_stats.level), 7)
        pyxel.text(70, 100, "<SPACE> COMPLETE LEVEL " + str(self.level_stats.level), 7)
