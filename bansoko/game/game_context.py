from .level import LevelStatistics
from .screens.choose_level import ChooseLevelScreen
from .screens.game import GameScreen
from .screens.game_paused import GamePausedScreen
from .screens.level_completed import LevelCompletedScreen
from .screens.main_menu import MainMenuScreen
from .screens.screen_factory import ScreenFactory
from ..gui.screen import Screen


class GameContext(ScreenFactory):
    def get_main_menu(self) -> Screen:
        return MainMenuScreen(self)

    def get_game_screen(self, level: int) -> Screen:
        return GameScreen(self, level)

    def get_choose_level_screen(self) -> Screen:
        return ChooseLevelScreen(self)

    def get_game_paused_screen(self, level: int) -> Screen:
        return GamePausedScreen(self, level)

    def get_level_completed_screen(self, level_stats: LevelStatistics) -> Screen:
        return LevelCompletedScreen(self, level_stats)
