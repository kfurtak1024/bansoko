"""
Module providing an abstraction over game screens creation.
"""
from abc import ABC, abstractmethod

from bansoko.game.level import LevelStatistics
from bansoko.gui.screen import Screen


class ScreenFactory(ABC):
    """
    An abstraction over game screen creation.
    By having this abstraction we're solving the problem with circular
    dependencies between screens.
    """

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
