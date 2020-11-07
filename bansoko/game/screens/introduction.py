"""Module defining game screen which is displayed before playing tutorial level."""

import pyxel

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.gui.menu import MenuScreen, TextMenuItem, Menu


class IntroductionScreen(MenuScreen):
    """Screen displayed before player starts tutorial level.

    Player can only go back to playfield screen from here.
    """

    def __init__(self, screen_factory: ScreenFactory):
        bundle = screen_factory.get_bundle()
        menu = Menu.with_defaults(tuple([
            TextMenuItem("OK", lambda: None)
        ]))
        super().__init__(menu=menu, background=bundle.get_background("introduction"),
                         semi_transparent=True, allow_going_back=True)

    def draw(self, draw_as_secondary: bool = False) -> None:
        super().draw(draw_as_secondary)
        pyxel.text(90, 60, "INTRODUCTION !!!\n\nWELCOME TO BANSOKO!!\n\nBLABLABLABLA", 7)
