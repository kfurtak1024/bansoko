"""Module defining game screen which is displayed before playing tutorial level."""

import pyxel

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.gui.menu import MenuScreen, TextMenuItem, Menu
from graphics import Point


class IntroductionScreen(MenuScreen):
    """Screen displayed before player starts tutorial level.

    Player can only go back to playfield screen from here.
    """

    def __init__(self, screen_factory: ScreenFactory):
        bundle = screen_factory.get_bundle()
        menu = Menu.with_defaults(tuple([
            TextMenuItem("OK", lambda: None)
        ]), position=Point(120, 176))
        super().__init__(menu=menu, background=bundle.get_background("introduction"),
                         semi_transparent=True, allow_going_back=True)

    def draw(self, draw_as_secondary: bool = False) -> None:
        super().draw(draw_as_secondary)
        pyxel.text(32, 56, "WELCOME TO BANSOKO!\n\n"
                           "LOREM IPSUM DOLOR SIT AMET, CONSECTETUR\n"
                           "ADIPISCING ELIT, SED DO EIUSMOD TEMPOR\n"
                           "INCIDIDUNT UT LABORE ET DOLORE MAGNA ALIQUA.\n"
                           "UT ENIM AD MINIM VENIAM, QUIS NOSTRUD\n"
                           "EXERCITATION ULLAMCO LABORIS NISI UT ALIQUIP\n"
                           "EX EA COMMODO CONSEQUAT. DUIS AUTE IRURE DOLOR\n"
                           "IN REPREHENDERIT IN VOLUPTATE VELIT ESSE CILLUM\n"
                           "DOLORE EU FUGIAT NULLA PARIATUR. EXCEPTEUR SINT\n"
                           "OCCAECAT CUPIDATAT NON PROIDENT, SUNT IN CULPA\n"
                           "QUI OFFICIA DESERUNT MOLLIT ANIM ID EST LABORUM.", 7)
