"""Module defining game screen which is displayed after finishing the last level."""

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.gui.menu import MenuController, TextMenuItem, Menu, MenuLayout


class VictoryController(MenuController):
    """Screen controller for displaying victory screen.

    It's displayed when player completes the last level (finishes the game).
    Player can only go back to main menu screen from here.
    """

    def __init__(self, screen_factory: ScreenFactory):
        screen = screen_factory.get_bundle().get_screen("victory")
        menu = Menu.with_defaults(tuple([
            TextMenuItem("MAIN MENU", screen_factory.get_main_menu)
        ]), MenuLayout(position=screen.menu_position))
        super().__init__(menu=menu, screen=screen)
