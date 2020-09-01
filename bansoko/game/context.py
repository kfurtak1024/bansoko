"""Module defining game context shared between all game screens."""

from bansoko.game.bundle import Bundle
from bansoko.game.level import LevelStatistics
from bansoko.game.profile import PlayerProfile
from bansoko.game.screens.choose_level import ChooseLevelScreen
from bansoko.game.screens.game_paused import GamePausedScreen
from bansoko.game.screens.level_completed import LevelCompletedScreen
from bansoko.game.screens.main_menu import MainMenuScreen
from bansoko.game.screens.playfield import PlayfieldScreen
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.game.screens.victory import VictoryScreen
from bansoko.gui.screen import Screen


class GameContext(ScreenFactory):
    """GameContext is a screen factory that is shared between all game screens."""

    def __init__(self, bundle: Bundle, player_profile: PlayerProfile):
        self.bundle = bundle
        self.player_profile = player_profile

    def get_bundle(self) -> Bundle:
        return self.bundle

    def get_player_profile(self) -> PlayerProfile:
        return self.player_profile

    def get_main_menu(self) -> Screen:
        return MainMenuScreen(self)

    def get_playfield_screen(self, level_num: int) -> Screen:
        return PlayfieldScreen(self, level_num)

    def get_choose_level_screen(self) -> Screen:
        return ChooseLevelScreen(self)

    def get_game_paused_screen(self, level_num: int) -> Screen:
        return GamePausedScreen(self, level_num)

    def get_level_completed_screen(self, level_stats: LevelStatistics) -> Screen:
        return LevelCompletedScreen(self, level_stats)

    def get_victory_screen(self) -> Screen:
        return VictoryScreen(self)
