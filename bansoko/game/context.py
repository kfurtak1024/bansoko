"""Module defining game context shared between all game screens."""
from typing import Callable

from bansoko.game.bundle import Bundle
from bansoko.game.profile import PlayerProfile, LevelScore
from bansoko.game.screens.choose_level import ChooseLevelController
from bansoko.game.screens.exit import ExitController
from bansoko.game.screens.game_paused import GamePausedController
from bansoko.game.screens.how_to_play import HowToPlayController
from bansoko.game.screens.level_completed import LevelCompletedController
from bansoko.game.screens.main_menu import MainMenuController
from bansoko.game.screens.playfield import PlayfieldScreen
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.game.screens.victory import VictoryController
from bansoko.gui.navigator import ScreenController


class GameContext(ScreenFactory):
    """GameContext is a screen factory that is shared between all game screens."""

    def __init__(self, bundle: Bundle, player_profile: PlayerProfile):
        self.bundle = bundle
        self.player_profile = player_profile

    def get_bundle(self) -> Bundle:
        return self.bundle

    def get_player_profile(self) -> PlayerProfile:
        return self.player_profile

    def get_main_menu(self) -> ScreenController:
        return MainMenuController(self)

    def get_playfield_screen(self, level_num: int,
                             skip_how_to_play: bool = False) -> ScreenController:
        skip_how_to_play = (level_num == 0) and not skip_how_to_play
        return PlayfieldScreen(self, level_num, show_how_to_play=skip_how_to_play)

    def get_choose_level_screen(self) -> ScreenController:
        return ChooseLevelController(self)

    def get_game_paused_screen(self, level_num: int) -> ScreenController:
        return GamePausedController(self, level_num)

    def get_level_completed_screen(self, level_score: LevelScore) -> ScreenController:
        return LevelCompletedController(self, level_score)

    def get_how_to_play_screen(self) -> ScreenController:
        return HowToPlayController(self)

    def get_victory_screen(self) -> ScreenController:
        return VictoryController(self)

    def get_exit_screen(self, exit_callback: Callable[[], None]) -> ScreenController:
        return ExitController(self, exit_callback)
