"""
Module exposing a main menu screen.
"""

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.gui.menu import MenuScreen, TextMenuItem
from graphics.text import draw_text, TextStyle


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
            TextMenuItem("START GAME", lambda: screen_factory.get_game_screen(0)),
            TextMenuItem("CHOOSE LEVEL", screen_factory.get_choose_level_screen),
            TextMenuItem("EXIT", lambda: None)
        ], background_color=0)

    def draw(self) -> None:
        super().draw()
        draw_text(80, 240, "(c) 2020 KRZYSZTOF FURTAK", TextStyle(color=7, shadow=True))
