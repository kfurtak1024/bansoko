"""
Module exposing a game screen which is displayed when game is paused.
"""
import pyxel

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.gui.menu import MenuItem, MenuScreen


class GamePausedScreen(MenuScreen):
    """
    This screen is displayed when player pauses the game.
    From this screen player can resume the game, restart the current level
    (restoring level to its initial state) or return back to the Main Menu.

    Arguments:
        screen_factory - used for creation of screens this screen will navigate to
    """

    def __init__(self, screen_factory: ScreenFactory, level: int):
        super().__init__([
            MenuItem("RESUME GAME", lambda: None),
            MenuItem("RESTART LEVEL", lambda: screen_factory.get_game_screen(level)),
            MenuItem("BACK TO MAIN MENU", screen_factory.get_main_menu)
        ], 1)

    def draw(self) -> None:
        super().draw()
        pyxel.text(16, 16, "GAME PAUSED", 7)
