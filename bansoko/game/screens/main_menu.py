"""
Module exposing a main menu screen.
"""
import pyxel

from .screen_factory import ScreenFactory
from ...gui.menu import MenuItem, MenuScreen


class MainMenuScreen(MenuScreen):
    """
    Main Menu for the game (entry point for the game).
    Screen allows player to start a new game, choose a level from a list of
    all unlocked levels or exit the game.

    Arguments:
        screen_factory - used for creation of screens this screen will navigate to
    """

    def __init__(self, screen_factory: ScreenFactory):
        super().__init__([
            MenuItem("START GAME", lambda: screen_factory.get_game_screen(1)),
            MenuItem("CHOOSE LEVEL", screen_factory.get_choose_level_screen),
            MenuItem("EXIT", lambda: None)
        ], 1)

    def draw(self) -> None:
        super().draw()
        pyxel.text(16, 16, "MAIN MENU", 7)
