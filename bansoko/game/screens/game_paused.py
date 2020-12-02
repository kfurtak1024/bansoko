"""Module defining screen controller which is displayed when game is paused."""

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.gui.menu import MenuController, TextMenuItem, Menu, MenuLayout


class GamePausedController(MenuController):
    """Screen controller for displaying pause menu in the game.

    From this screen player can resume the game, restart the current level
    (restoring level to its initial state) display How To Play instructions or return back to
    the Main Menu.
    """

    def __init__(self, screen_factory: ScreenFactory, level_num: int):
        screen = screen_factory.get_bundle().get_screen("game_paused")
        menu = Menu.with_defaults((
            TextMenuItem("RESUME GAME", lambda: None),
            TextMenuItem("RESTART LEVEL", lambda: screen_factory.get_playfield_screen(
                level_num, skip_how_to_play=True)),
            TextMenuItem("HOW TO PLAY", screen_factory.get_how_to_play_screen),
            TextMenuItem("MAIN MENU", screen_factory.get_main_menu)
        ), MenuLayout(position=screen.menu_position))
        super().__init__(menu=menu, allow_going_back=True, screen=screen, semi_transparent=True)
