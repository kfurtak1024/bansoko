from abc import ABC, abstractmethod

from game.level import LevelStatistics
from gui.screen import Screen


class ScreenFactory(ABC):
    @abstractmethod
    def get_main_menu(self) -> Screen:
        """Create a new instance of MainMenuScreen"""

    @abstractmethod
    def get_game_screen(self, level: int) -> Screen:
        """Create a new instance of GameScreen"""

    @abstractmethod
    def get_choose_level_screen(self) -> Screen:
        """Create a new instance of ChooseLevelScreen"""

    @abstractmethod
    def get_game_paused_screen(self, level: int) -> Screen:
        """Create a new instance of GamePausedScreen"""

    @abstractmethod
    def get_level_completed_screen(self, level_stats: LevelStatistics) -> Screen:
        """Create a new instance of LevelCompletedScreen"""
