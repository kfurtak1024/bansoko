"""Module defining game screen for choosing a level to be played."""
from typing import Optional

import pyxel

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics.background import Background
from bansoko.gui.menu import MenuScreen, TextMenuItem


class LevelMenuItem(TextMenuItem):
    def __init__(self, level_num: int, screen_factory: ScreenFactory):
        super().__init__(
            "LEVEL " + str(level_num + 1),
            lambda: screen_factory.get_playfield_screen(level_num))


class ChooseLevelScreen(MenuScreen):
    """
    Screen allowing player to choose a level to play.
    Player can choose a level from all unlocked levels (Level is "unlocked"
    when its predecessor level is completed)
    From this screen it is also possible to navigate back to Main Menu.

    Arguments:
        screen_factory - used for creation of screens this screen will navigate to
        num_levels - total number of available levels
        background - background to be drawn for this screen
    """

    def __init__(self, screen_factory: ScreenFactory, num_levels: int,
                 background: Optional[Background]):
        super().__init__([
            LevelMenuItem(level_num, screen_factory) for level_num in range(num_levels)
        ], columns=5, allow_going_back=True, background=background)

    def draw(self) -> None:
        super().draw()
        pyxel.text(8, 8, "CHOOSE LEVEL", 7)
