"""Module defining game screen which is displayed when level is completed."""
from typing import Optional, List

import pyxel

from bansoko.game.level import LevelStatistics
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics.background import Background
from bansoko.gui.menu import MenuScreen, TextMenuItem, MenuItem


class LevelCompletedScreen(MenuScreen):
    """
    Screen displayed when player completes the level.
    Player can navigate to the next level, replay the current level
    (to get better score) or get back to Main Menu.

    Arguments:
        screen_factory - used for creation of screens this screen will navigate to
        level_stats - statistics of level completion
        last_level_completed - is completed level the last one
        background - background to be drawn for this screen
    """

    def __init__(self, screen_factory: ScreenFactory, level_stats: LevelStatistics,
                 last_level_completed: bool, background: Optional[Background]):
        current_level_num = level_stats.level_num
        next_level_num = current_level_num + 1

        next_level = TextMenuItem(
            "PLAY NEXT LEVEL", lambda: screen_factory.get_playfield_screen(next_level_num))
        finish_game = TextMenuItem(
            "FINISH GAME", lambda: screen_factory.get_victory_screen())
        restart_level = TextMenuItem(
            "RESTART LEVEL", lambda: screen_factory.get_playfield_screen(current_level_num))
        go_back = TextMenuItem(
            "BACK TO MAIN MENU", lambda: screen_factory.get_main_menu())

        more_levels_to_play_menu: List[MenuItem] = [next_level, restart_level, go_back]
        last_level_finished_menu: List[MenuItem] = [finish_game, restart_level]
        menu = last_level_finished_menu if last_level_completed else more_levels_to_play_menu

        super().__init__(menu, background=background)
        self.level_stats = level_stats

    def draw(self) -> None:
        super().draw()
        pyxel.text(16, 16, "LEVEL " + str(self.level_stats.level_num + 1) + " COMPLETED", 7)
