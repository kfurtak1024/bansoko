"""
Module exposing a main menu screen.
"""
from typing import Optional

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics.background import Background
from bansoko.graphics.text import draw_text, TextStyle
from bansoko.gui.menu import MenuScreen, TextMenuItem


class MainMenuScreen(MenuScreen):
    """
    Main Menu for the game (entry point for the game).
    Screen allows player to start a new game, choose a level from a list of
    all unlocked levels or exit the game.

    Arguments:
        screen_factory - used for creation of screens this screen will navigate to
        background - background to be drawn for this screen
    """

    def __init__(self, screen_factory: ScreenFactory, background: Optional[Background]):
        super().__init__([
            TextMenuItem("START GAME", lambda: screen_factory.get_playfield_screen(0)),
            TextMenuItem("CHOOSE LEVEL", screen_factory.get_choose_level_screen),
            TextMenuItem("EXIT", lambda: None)
        ], background=background)

    def draw(self) -> None:
        super().draw()
        draw_text(80, 240, "(c) 2020 KRZYSZTOF FURTAK", TextStyle(color=7, shadow=True))
