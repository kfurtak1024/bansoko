"""Module defining game screen which is displayed after finishing the last level."""

import pyxel

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.gui.menu import MenuScreen, TextMenuItem, MenuConfig


class VictoryScreen(MenuScreen):
    """Screen displayed when player completes the last level (finished the game).

    Player can only go back to main menu screen from here.
    """

    def __init__(self, screen_factory: ScreenFactory):
        bundle = screen_factory.get_bundle()
        super().__init__((
            TextMenuItem("BACK TO MAIN MENU", screen_factory.get_main_menu),
        ), MenuConfig(background=bundle.get_background("victory")))

    def draw(self) -> None:
        super().draw()
        pyxel.text(90, 60, "CONGRATULATIONS !!!\n\n    YOU WON !!!", 7)
