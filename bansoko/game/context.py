from bansoko.game.level import LevelStatistics
from bansoko.game.screens.choose_level import ChooseLevelScreen
from bansoko.game.screens.game_paused import GamePausedScreen
from bansoko.game.screens.level_completed import LevelCompletedScreen
from bansoko.game.screens.main_menu import MainMenuScreen
from bansoko.game.screens.playfield import PlayfieldScreen
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.gui.screen import Screen
from game.bundle import Bundle
from game.core import Level


class GameContext(ScreenFactory):
    def __init__(self, bundle: Bundle):
        self.bundle = bundle

    def get_main_menu(self) -> Screen:
        return MainMenuScreen(self, self.bundle.get_background("main_menu"))

    def get_playfield_screen(self, level: int) -> Screen:
        return PlayfieldScreen(self, Level(self.bundle.get_level_template(level)),
                               self.bundle.get_background("playfield"))

    def get_choose_level_screen(self) -> Screen:
        return ChooseLevelScreen(self, self.bundle.get_background("choose_level"))

    def get_game_paused_screen(self, level: int) -> Screen:
        return GamePausedScreen(self, level, self.bundle.get_background("game_paused"))

    def get_level_completed_screen(self, level_stats: LevelStatistics) -> Screen:
        return LevelCompletedScreen(self, level_stats,
                                    self.bundle.get_background("level_completed"))
