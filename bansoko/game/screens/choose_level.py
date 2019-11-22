"""
Module exposing a game screen for choosing a level to be played.
"""
import pyxel

from .screen_factory import ScreenFactory
from ...gui.menu import MenuItem, MenuScreen


class ChooseLevelScreen(MenuScreen):
    """
    Screen allowing player to choose a level to play.
    Player can choose a level from all unlocked levels (Level is "unlocked"
    when its predecessor level is completed)
    From this screen it is also possible to navigate back to Main Menu.

    Arguments:
        screen_factory - used for creation of screens this screen will navigate to
    """

    def __init__(self, screen_factory: ScreenFactory):
        super().__init__([
            MenuItem("START LEVEL", lambda: screen_factory.get_game_screen(1)),
            MenuItem("BACK TO MAIN MENU", lambda: None)
        ], 1)

    def draw(self) -> None:
        super().draw()
        pyxel.text(16, 16, "CHOOSE LEVEL", 7)
