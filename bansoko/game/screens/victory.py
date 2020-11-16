"""Module defining game screen which is displayed after finishing the last level."""

import pyxel

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.gui.menu import MenuController, TextMenuItem, Menu


class VictoryController(MenuController):
    """Screen controller for displaying victory screen.

    It's displayed when player completes the last level (finishes the game).
    Player can only go back to main menu screen from here.
    """

    def __init__(self, screen_factory: ScreenFactory):
        bundle = screen_factory.get_bundle()
        menu = Menu.with_defaults(tuple([
            TextMenuItem("BACK TO MAIN MENU", screen_factory.get_main_menu)
        ]))
        super().__init__(menu=menu, background=bundle.get_background("victory"))

    def draw(self, draw_as_secondary: bool = False) -> None:
        super().draw(draw_as_secondary)
        # TODO: Those should belong to resources file!
        pyxel.text(90, 60, "CONGRATULATIONS !!!\n\n    YOU WON !!!", 7)
