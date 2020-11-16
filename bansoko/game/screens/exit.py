"""Module defining game screen which is displayed before exiting the game."""
from typing import Callable

import pyxel

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point
from bansoko.gui.menu import MenuScreen, TextMenuItem, Menu


class ExitScreen(MenuScreen):
    """Screen displayed when player wants to exit the game.

    It displays confirmation dialog.
    """

    def __init__(self, screen_factory: ScreenFactory, exit_callback: Callable):
        bundle = screen_factory.get_bundle()
        menu = Menu.with_defaults(tuple([
            # TODO: Add horizontal space to menu items (so no spaces will be needed)
            TextMenuItem("YES  ", self._exit),
            TextMenuItem("NO  ", lambda: None)
        ]), columns=2, position=Point(98, 132))
        super().__init__(
            menu=menu,
            allow_going_back=True,
            background=bundle.get_background("exit"),
            semi_transparent=True)
        self.exit_callback = exit_callback

    def draw(self, draw_as_secondary: bool = False) -> None:
        super().draw(draw_as_secondary)
        # TODO: Those should belong to resources file!
        pyxel.text(60, 118, "ARE YOU SURE DO YOU WANT TO EXIT?", 7)

    def _exit(self) -> None:
        self.exit_callback()
