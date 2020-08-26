"""Module defining game context shared between all game screens."""
from bansoko.game.bundle import Bundle
from bansoko.game.level import LevelStatistics, Level
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

    def __init__(self, bundle: Bundle):
        self.bundle = bundle

    def get_main_menu(self) -> Screen:
        return MainMenuScreen(self, self.bundle.get_background("main_menu"))

    def get_playfield_screen(self, level: int) -> Screen:
        level = Level(self.bundle.get_level_template(level), self.bundle.get_robot_skin(),
                      self.bundle.get_crate_skin())
        return PlayfieldScreen(self, level, self.bundle.get_background("playfield"))

    def get_choose_level_screen(self) -> Screen:
        return ChooseLevelScreen(self, self.bundle.num_levels,
                                 self.bundle.get_background("choose_level"))

    def get_game_paused_screen(self, level: int) -> Screen:
        return GamePausedScreen(self, level, self.bundle.get_background("game_paused"))

    def get_level_completed_screen(self, level_stats: LevelStatistics) -> Screen:
        return LevelCompletedScreen(self, level_stats,
                                    level_stats.level_num == self.bundle.last_level,
                                    self.bundle.get_background("level_completed"))

    def get_victory_screen(self) -> Screen:
        return VictoryScreen(self, self.bundle.get_background("victory"))
