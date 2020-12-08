"""Module for handling critical game errors."""
import textwrap

import pyxel

from bansoko import GAME_FRAME_TIME_IN_MS
from bansoko.graphics import Point, center_in_rect, Rect
from bansoko.graphics.text import draw_text, text_size
from bansoko.gui.menu import MenuController, Menu, TextMenuItem, MenuLayout
from bansoko.gui.navigator import ScreenNavigator

PADDING = Point(8, 8)


class ErrorScreen(MenuController):
    """Screen controller for displaying game critical errors.

    It's displayed when a non-recoverable error occurs during game startup.
    """

    def __init__(self, message: str):
        self.error_message = self._build_error_message(message)
        self.frame_rect = self._get_frame_rect(self.error_message)
        menu = Menu.with_defaults(tuple([
            TextMenuItem("OK", lambda: None)
        ]), MenuLayout(position=self._get_menu_position(self.frame_rect)))
        super().__init__(menu=menu)

    def draw(self, draw_as_secondary: bool = False) -> None:
        self._draw_background()
        self._draw_frame()
        super().draw(draw_as_secondary=draw_as_secondary)

    def _draw_frame(self) -> None:
        pyxel.rectb(self.frame_rect.x, self.frame_rect.y, self.frame_rect.w, self.frame_rect.h, 8)
        pyxel.rect(self.frame_rect.x + 1, self.frame_rect.y + 1, self.frame_rect.w - 2,
                   self.frame_rect.h - 2, 2)
        draw_text(self.frame_rect.position.offset(PADDING), self.error_message)

    @staticmethod
    def _draw_background() -> None:
        for i in range(7, 255, 16):
            pyxel.line(i, 0, i, 255, 1)
            pyxel.line(0, i, 255, i, 1)

    @staticmethod
    def _build_error_message(message: str) -> str:
        wrapped_message = "\n".join(textwrap.wrap(message, 50))
        return f"#E** ERROR **#7\n\n{wrapped_message}\n\nPlease check logs for more details."

    @staticmethod
    def _get_frame_rect(message: str) -> Rect:
        return center_in_rect(text_size(message).enlarge(
            2 * PADDING.x, 2 * PADDING.y + 3 * pyxel.FONT_HEIGHT))

    @staticmethod
    def _get_menu_position(frame_rect: Rect) -> Point:
        return Point(-1, frame_rect.bottom - PADDING.y - pyxel.FONT_HEIGHT)


def show_error_message(message: str) -> None:
    """Display an error screen with a message from which player can only quit the game.

    :param message: error message to be displayed
    """
    navigator = ScreenNavigator(ErrorScreen(message), pyxel.quit, GAME_FRAME_TIME_IN_MS)
    pyxel.run(navigator.update, navigator.draw)
