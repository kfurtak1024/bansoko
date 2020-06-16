from typing import List

from bansoko.game.level import LevelStatistics, Level, LevelTemplate, NUM_LEVELS
from bansoko.game.screens.choose_level import ChooseLevelScreen
from bansoko.game.screens.game import GameScreen
from bansoko.game.screens.game_paused import GamePausedScreen
from bansoko.game.screens.level_completed import LevelCompletedScreen
from bansoko.game.screens.main_menu import MainMenuScreen
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.gui.screen import Screen


class GameContext(ScreenFactory):
    level_templates: List[LevelTemplate]

    def __init__(self):
        self.level_templates = [LevelTemplate(level_num) for level_num in range(NUM_LEVELS)]

    def get_main_menu(self) -> Screen:
        return MainMenuScreen(self)

    def get_game_screen(self, level: int) -> Screen:
        return GameScreen(self, Level(self.level_templates[level]))

    def get_choose_level_screen(self) -> Screen:
        return ChooseLevelScreen(self)

    def get_game_paused_screen(self, level: int) -> Screen:
        return GamePausedScreen(self, level)

    def get_level_completed_screen(self, level_stats: LevelStatistics) -> Screen:
        return LevelCompletedScreen(self, level_stats)
