"""Module defining screen controller which is displayed before exiting the game."""
from typing import Callable

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Size
from bansoko.gui.menu import MenuController, TextMenuItem, Menu, MenuLayout


class ExitController(MenuController):
    """Screen controller for displaying exit confirmation dialog."""

    def __init__(self, screen_factory: ScreenFactory, exit_callback: Callable[[], None]):
        screen = screen_factory.get_bundle().get_screen("exit")
        menu = Menu.with_defaults(tuple([
            TextMenuItem("YES", self._exit),
            TextMenuItem("NO", lambda: None)
        ]), MenuLayout(columns=2, position=screen.menu_position, item_space=Size(8, 0)))
        super().__init__(menu=menu, allow_going_back=True, screen=screen, semi_transparent=True)
        self.exit_callback = exit_callback

    def _exit(self) -> None:
        self.exit_callback()
