"""Module for handling critical game errors."""
import pyxel

from bansoko import GAME_FRAME_TIME_IN_MS
from bansoko.graphics import Point
from bansoko.graphics.text import draw_text
from bansoko.gui.menu import MenuController, Menu, TextMenuItem, MenuLayout
from bansoko.gui.navigator import ScreenNavigator


class ErrorScreen(MenuController):
    """Screen controller for displaying game critical errors.

    It's displayed when a non-recoverable error occurs during game startup.
    """

    def __init__(self, message: str):
        menu = Menu.with_defaults(tuple([
            TextMenuItem("OK", lambda: None)
        ]), MenuLayout(position=Point(100, 100)))
        super().__init__(menu=menu)
        self.message = message

    def draw(self, draw_as_secondary: bool = False) -> None:
        super().draw(draw_as_secondary=draw_as_secondary)
        draw_text(Point(10, 10), "ERROR: " + self.message)
        # TODO: Work on look&feel of this screen


def show_error_message(message: str) -> None:
    """Display an error screen with a message from which player can only quit the game.

    :param message: error message to be displayed
    """
    navigator = ScreenNavigator(ErrorScreen(message), pyxel.quit, GAME_FRAME_TIME_IN_MS)
    pyxel.run(navigator.update, navigator.draw)
