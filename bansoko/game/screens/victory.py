"""Module defining game screen which is displayed after finishing the last level."""
from typing import Optional

import pyxel

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics.background import Background
from bansoko.gui.menu import MenuScreen, TextMenuItem


class VictoryScreen(MenuScreen):
    """
    Screen displayed when player completes the last level (finished the game).
    Player can only go back to main menu screen from here.

    Arguments:
        screen_factory - used for creation of screens this screen will navigate to
        background - background to be drawn for this screen
    """

    def __init__(self, screen_factory: ScreenFactory, background: Optional[Background]):
        super().__init__([
            TextMenuItem("BACK TO MAIN MENU", screen_factory.get_main_menu)
        ], background=background)

    def draw(self) -> None:
        super().draw()
        pyxel.text(90, 60, "CONGRATULATIONS !!!\n\n    YOU WON !!!", 7)
