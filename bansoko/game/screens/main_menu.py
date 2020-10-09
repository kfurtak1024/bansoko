"""Module defining main menu screen."""

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point
from bansoko.graphics.text import draw_text, TextStyle
from bansoko.gui.menu import MenuScreen, TextMenuItem, MenuConfig


class MainMenuScreen(MenuScreen):
    """Main Menu for the game (entry point for the game).

    Screen allows player to start a new game, choose a level from a list of
    all unlocked levels or exit the game.
    """

    def __init__(self, screen_factory: ScreenFactory):
        level_to_play = screen_factory.get_player_profile().first_not_completed_level
        super().__init__((
            TextMenuItem("START GAME", lambda: screen_factory.get_playfield_screen(level_to_play)),
            TextMenuItem("CHOOSE LEVEL", screen_factory.get_choose_level_screen),
            TextMenuItem("EXIT", lambda: None)
        ), config=MenuConfig(background=screen_factory.get_bundle().get_background("main_menu")))

    def draw(self, draw_as_secondary: bool = False) -> None:
        super().draw(draw_as_secondary)
        draw_text(Point(80, 240), "(c) 2020 KRZYSZTOF FURTAK", TextStyle(color=7, shadow_color=1))
