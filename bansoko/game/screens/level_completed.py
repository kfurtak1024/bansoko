"""
Module exposing a game screen which is displayed when level is completed.
"""
import pyxel

from bansoko.game.level import LevelStatistics
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.gui.menu import MenuScreen, TextMenuItem
from graphics.background import Background


class LevelCompletedScreen(MenuScreen):
    """
    Screen displayed when player completes the level.
    Player can navigate to the next level, replay the current level
    (to get better score) or get back to Main Menu.

    Arguments:
        screen_factory - used for creation of screens this screen will navigate to
        level_stats - statistics of level completion
        background - background to be drawn for this screen
    """

    def __init__(self, screen_factory: ScreenFactory, level_stats: LevelStatistics,
                 background: Background):
        current_level = level_stats.level_num
        next_level = current_level + 1
        super().__init__([
            TextMenuItem("PLAY NEXT LEVEL", lambda: screen_factory.get_playfield_screen(next_level)),
            TextMenuItem("RESTART LEVEL", lambda: screen_factory.get_playfield_screen(current_level)),
            TextMenuItem("BACK TO MAIN MENU", screen_factory.get_main_menu)
        ], background=background)
        self.level_stats = level_stats

    def draw(self) -> None:
        super().draw()
        pyxel.text(16, 16, "LEVEL " + str(self.level_stats.level_num + 1) + " COMPLETED", 7)
