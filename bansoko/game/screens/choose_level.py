"""Module defining game screen for choosing a level to be played."""
from typing import Optional

import pyxel

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point
from bansoko.gui.menu import MenuScreen, TextMenuItem
from bansoko.gui.screen import Screen


class LevelMenuItem(TextMenuItem):
    def __init__(self, level_num: int, screen_factory: ScreenFactory):
        super().__init__(
            "LEVEL " + str(level_num + 1),
            lambda: screen_factory.get_playfield_screen(level_num))
        self.level_num = level_num
        self.player_profile = screen_factory.get_player_profile()

    def draw(self, position: Point, selected: bool = False) -> None:
        super().draw(position, selected)
        if selected:
            text = ""
            if not self.player_profile.is_level_unlocked(self.level_num):
                text = "LOCKED"
            elif not self.player_profile.is_level_completed(self.level_num):
                text = "NOT COMPLETED"
            else:
                level_stats = self.player_profile.level_stats[self.level_num]
                if level_stats:
                    text = level_stats.debug_description

            pyxel.text(8, 220, f"LEVEL STATS:\n============\n{text}", 10)

    def perform_action(self) -> Optional[Screen]:
        # TODO: Disallow playing locked levels!
        return super().perform_action()


class ChooseLevelScreen(MenuScreen):
    """Screen allowing player to choose a level to play.

    Player can choose a level from all unlocked levels (Level is "unlocked"
    when its predecessor level is completed)
    From this screen it is also possible to navigate back to Main Menu.
    """

    def __init__(self, screen_factory: ScreenFactory):
        bundle = screen_factory.get_bundle()
        super().__init__([
            LevelMenuItem(level_num, screen_factory) for level_num in range(bundle.num_levels)
        ], columns=5, allow_going_back=True, background=bundle.get_background("choose_level"))

    def draw(self) -> None:
        super().draw()
        pyxel.text(8, 8, "CHOOSE LEVEL", 7)
