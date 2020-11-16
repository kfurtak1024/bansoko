"""Module defining main menu screen."""
from typing import Optional

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point
from bansoko.graphics.text import draw_text, TextStyle
from bansoko.gui.menu import MenuScreen, TextMenuItem, Menu
from bansoko.gui.screen import Screen


class MainMenuScreen(MenuScreen):
    """Main Menu for the game (entry point for the game).

    Screen allows player to start a new game, choose a level from a list of
    all unlocked levels or exit the game.
    """

    def __init__(self, screen_factory: ScreenFactory):
        self.exiting = False
        self._get_exit_screen = lambda: screen_factory.get_exit_screen(self._exit_callback)
        level_to_play = screen_factory.get_player_profile().first_not_completed_level
        menu = Menu.with_defaults((
            TextMenuItem("START GAME", lambda: screen_factory.get_playfield_screen(level_to_play)),
            TextMenuItem("CHOOSE LEVEL", screen_factory.get_choose_level_screen),
            TextMenuItem("EXIT", self._get_exit_screen)))
        super().__init__(
            menu=menu,
            allow_going_back=True,
            background=screen_factory.get_bundle().get_background("main_menu"))

    def activate(self) -> None:
        super().activate()
        self.select_and_scroll_to_item(0)

    def draw(self, draw_as_secondary: bool = False) -> None:
        super().draw(draw_as_secondary)
        draw_text(Point(79, 240), "(c) 2020 KRZYSZTOF FURTAK", TextStyle(color=7, shadow_color=1))

    def update(self, dt_in_ms: float) -> Optional[Screen]:
        if self.exiting:
            return None
        screen_to_go_to = super().update(dt_in_ms)
        return screen_to_go_to if screen_to_go_to else self._get_exit_screen()

    def _exit_callback(self) -> None:
        self.exiting = True
