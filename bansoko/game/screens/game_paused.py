"""Module defining a game screen which is displayed when game is paused."""

import pyxel

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.gui.menu import MenuScreen, TextMenuItem


class GamePausedScreen(MenuScreen):
    """
    This screen is displayed when player pauses the game.
    From this screen player can resume the game, restart the current level
    (restoring level to its initial state) or return back to the Main Menu.

    Arguments:
        screen_factory - used for creation of screens this screen will navigate to
        level_num- currently played level
    """

    def __init__(self, screen_factory: ScreenFactory, level_num: int):
        bundle = screen_factory.get_bundle()
        super().__init__([
            TextMenuItem("RESUME GAME", lambda: None),
            TextMenuItem("RESTART LEVEL", lambda: screen_factory.get_playfield_screen(level_num)),
            TextMenuItem("BACK TO MAIN MENU", screen_factory.get_main_menu)
        ], allow_going_back=True, background=bundle.get_background("game_paused"))

    def draw(self) -> None:
        super().draw()
        pyxel.text(16, 16, "GAME PAUSED", 7)
