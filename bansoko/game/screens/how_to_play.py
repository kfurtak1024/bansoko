"""Module defining game screen containing information on how to play."""

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.gui.menu import MenuController, TextMenuItem, Menu, MenuLayout


class HowToPlayController(MenuController):
    """Screen controller for displaying how to play instructions.

    Player can only go back to playfield screen from here.
    """

    def __init__(self, screen_factory: ScreenFactory):
        screen = screen_factory.get_bundle().get_screen("how_to_play")
        menu = Menu.with_defaults(tuple([
            TextMenuItem("OK", lambda: None)
        ]), MenuLayout(position=screen.menu_position))
        super().__init__(menu=menu, allow_going_back=True, screen=screen, semi_transparent=True)
