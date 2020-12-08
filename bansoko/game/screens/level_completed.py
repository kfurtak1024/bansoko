"""Module defining game screen which is displayed when level is completed."""
from typing import Tuple

from bansoko.game.profile import LevelScore
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point
from bansoko.graphics.text import draw_text
from bansoko.gui.menu import MenuController, TextMenuItem, MenuItem, Menu, MenuLayout

LEVEL_TIME_POS = Point(104, 75)
LEVEL_PUSHES_POS = Point(104, 84)
LEVEL_STEPS_POS = Point(104, 93)


class LevelCompletedController(MenuController):
    """Screen controller allowing player to choose what to do after completion of the level.

    Player can navigate to the next level, replay the current level
    (to get better score) or get back to Main Menu.
    """

    def __init__(self, screen_factory: ScreenFactory, level_score: LevelScore):
        current_level_num = level_score.level_num
        last_level_completed = current_level_num == screen_factory.get_bundle().last_level

        next_level = TextMenuItem(
            "PLAY NEXT LEVEL", lambda: screen_factory.get_playfield_screen(
                screen_factory.get_player_profile().next_level_to_play(current_level_num)))
        finish_game = TextMenuItem(
            "FINISH GAME", screen_factory.get_victory_screen)
        restart_level = TextMenuItem(
            "RESTART LEVEL", lambda: screen_factory.get_playfield_screen(
                current_level_num, skip_how_to_play=True))
        main_menu = TextMenuItem(
            "BACK TO MAIN MENU", screen_factory.get_main_menu)

        more_levels_to_play_menu: Tuple[MenuItem, ...] = (next_level, restart_level, main_menu)
        last_level_finished_menu: Tuple[MenuItem, ...] = (finish_game, restart_level)
        screen = screen_factory.get_bundle().get_screen("level_completed")
        menu = Menu.with_defaults(
            last_level_finished_menu if last_level_completed else more_levels_to_play_menu,
            MenuLayout(position=screen.menu_position))

        super().__init__(menu=menu, screen=screen, semi_transparent=True)
        player_profile = screen_factory.get_player_profile()
        self.level_score = level_score
        self.prev_level_score = player_profile.complete_level(level_score)

    def draw(self, draw_as_secondary: bool = False) -> None:
        super().draw(draw_as_secondary)
        self._draw_level_statistics()

    def _draw_level_statistics(self) -> None:
        new_record = "(NEW RECORD)"
        time_beaten = self.level_score.time_in_ms < self.prev_level_score.time_in_ms
        pushes_beaten = self.level_score.pushes < self.prev_level_score.pushes
        steps_beaten = self.level_score.steps < self.prev_level_score.steps
        first_completion = not self.prev_level_score.completed

        draw_text(LEVEL_TIME_POS, "#0{:>7s} #8{:s}".format(
            self.level_score.time, new_record if time_beaten or first_completion else ""))
        draw_text(LEVEL_PUSHES_POS, "#0{:>7d} #8{:s}".format(
            self.level_score.pushes, new_record if pushes_beaten or first_completion else ""))
        draw_text(LEVEL_STEPS_POS, "#0{:>7d} #8{:s}".format(
            self.level_score.steps, new_record if steps_beaten or first_completion else ""))
