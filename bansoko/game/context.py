from typing import List

from bansoko.game.level import LevelStatistics, LevelTemplate
from bansoko.game.screens.choose_level import ChooseLevelScreen
from bansoko.game.screens.game_paused import GamePausedScreen
from bansoko.game.screens.level_completed import LevelCompletedScreen
from bansoko.game.screens.main_menu import MainMenuScreen
from bansoko.game.screens.playfield import PlayfieldScreen
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.gui.screen import Screen
from game.core import Level
from game.tiles import TileSet


class GameContext(ScreenFactory):
    level_templates: List[LevelTemplate] = []

    def __init__(self, metadata):
        # TODO: Level templates should be initialized in a different place
        for level_num, level in enumerate(metadata["levels"]):
            self.level_templates.append(LevelTemplate(level_num, TileSet(level["tiles"])))

    def get_main_menu(self) -> Screen:
        return MainMenuScreen(self)

    def get_playfield_screen(self, level: int) -> Screen:
        return PlayfieldScreen(self, Level(self.level_templates[level]))

    def get_choose_level_screen(self) -> Screen:
        return ChooseLevelScreen(self)

    def get_game_paused_screen(self, level: int) -> Screen:
        return GamePausedScreen(self, level)

    def get_level_completed_screen(self, level_stats: LevelStatistics) -> Screen:
        return LevelCompletedScreen(self, level_stats)
