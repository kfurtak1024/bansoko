"""Module defining game screen which is displayed when level is completed."""
from typing import Tuple

import pyxel

from bansoko.game.profile import LevelScore
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point
from bansoko.graphics.text import draw_text
from bansoko.gui.menu import MenuScreen, TextMenuItem, MenuItem, MenuConfig


class LevelCompletedScreen(MenuScreen):
    """Screen displayed when player completes the level.

    Player can navigate to the next level, replay the current level
    (to get better score) or get back to Main Menu.
    """

    def __init__(self, screen_factory: ScreenFactory, level_score: LevelScore):
        current_level_num = level_score.level_num
        next_level_num = current_level_num + 1
        last_level_completed = current_level_num == screen_factory.get_bundle().last_level

        next_level = TextMenuItem(
            "PLAY NEXT LEVEL", lambda: screen_factory.get_playfield_screen(next_level_num))
        finish_game = TextMenuItem(
            "FINISH GAME", screen_factory.get_victory_screen)
        restart_level = TextMenuItem(
            "RESTART LEVEL", lambda: screen_factory.get_playfield_screen(current_level_num))
        go_back = TextMenuItem(
            "BACK TO MAIN MENU", screen_factory.get_main_menu)

        more_levels_to_play_menu: Tuple[MenuItem, ...] = (next_level, restart_level, go_back)
        last_level_finished_menu: Tuple[MenuItem, ...] = (finish_game, restart_level)
        menu = last_level_finished_menu if last_level_completed else more_levels_to_play_menu

        background = screen_factory.get_bundle().get_background("level_completed")
        super().__init__(menu, config=MenuConfig(background=background, semi_transparent=True))
        player_profile = screen_factory.get_player_profile()
        self.level_score = level_score
        self.prev_level_score = player_profile.complete_level(level_score)

    def draw(self, draw_as_secondary: bool = False) -> None:
        super().draw(draw_as_secondary)
        pyxel.rect(56, 48, 144, 64, 7)
        pyxel.text(95, 57, "LEVEL " + str(self.level_score.level_num + 1) + " COMPLETED", 3)
        self._draw_level_statistics()

    def _draw_level_statistics(self) -> None:
        new_record = "(NEW RECORD)"
        time_beaten = self.level_score.time_in_ms < self.prev_level_score.time_in_ms
        pushes_beaten = self.level_score.pushes < self.prev_level_score.pushes
        steps_beaten = self.level_score.steps < self.prev_level_score.steps

        draw_text(
            Point(72, 75),
            "#DTIME:   #0{:>7s} #8{:s}\n"
            "#DPUSHES: #0{:>7d} #8{:s}\n"
            "#DSTEPS:  #0{:>7d} #8{:s}".format(
                self.level_score.time, new_record if time_beaten else "",
                self.level_score.pushes, new_record if pushes_beaten else "",
                self.level_score.steps, new_record if steps_beaten else ""))
