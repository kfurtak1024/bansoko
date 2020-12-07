"""Module defining screen controller which is displayed when game is paused."""
from typing import Tuple

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.gui.menu import MenuController, TextMenuItem, Menu, MenuLayout, MenuItem


class GamePausedController(MenuController):
    """Screen controller for displaying pause menu in the game.

    From this screen player can resume the game, restart the current level
    (restoring level to its initial state) display How To Play instructions or return back to
    the Main Menu.
    """

    def __init__(self, screen_factory: ScreenFactory, level_num: int):
        screen = screen_factory.get_bundle().get_screen("game_paused")
        playing_last_level = level_num == screen_factory.get_bundle().last_level
        resume_game = TextMenuItem("RESUME GAME", lambda: None)
        restart_level = TextMenuItem("RESTART LEVEL", lambda: screen_factory.get_playfield_screen(
            level_num, skip_how_to_play=True))
        skip_level = TextMenuItem("SKIP LEVEL", lambda: screen_factory.get_playfield_screen(
            screen_factory.get_player_profile().next_level_to_play(level_num)))
        how_to_play = TextMenuItem("HOW TO PLAY", screen_factory.get_how_to_play_screen)
        main_menu = TextMenuItem("BACK TO MAIN MENU", screen_factory.get_main_menu)

        before_last_level_menu: Tuple[MenuItem, ...] = \
            (resume_game, restart_level, skip_level, how_to_play, main_menu)
        last_level_menu: Tuple[MenuItem, ...] = \
            (resume_game, restart_level, how_to_play, main_menu)

        menu = Menu.with_defaults(
            last_level_menu if playing_last_level else before_last_level_menu,
            MenuLayout(position=screen.menu_position))
        super().__init__(menu=menu, allow_going_back=True, screen=screen, semi_transparent=True)

    def draw(self, draw_as_secondary: bool = False) -> None:
        if not draw_as_secondary:
            super().draw(draw_as_secondary=draw_as_secondary)
