"""Module providing an abstraction over game screens creation."""
from abc import ABC, abstractmethod
from typing import Callable

from bansoko.game.bundle import Bundle
from bansoko.game.profile import PlayerProfile, LevelScore
from bansoko.gui.screen import Screen


class ScreenFactory(ABC):
    """An abstraction over game screen creation.

    By having this abstraction we're solving the problem with circular
    dependencies between screens.
    """

    @abstractmethod
    def get_bundle(self) -> Bundle:
        """..."""

    @abstractmethod
    def get_player_profile(self) -> PlayerProfile:
        """..."""

    @abstractmethod
    def get_main_menu(self) -> Screen:
        """Create a new instance of MainMenu screen"""

    @abstractmethod
    def get_playfield_screen(self, level_num: int) -> Screen:
        """Create a new instance of Playfield screen"""

    @abstractmethod
    def get_choose_level_screen(self) -> Screen:
        """Create a new instance of ChooseLevel screen"""

    @abstractmethod
    def get_game_paused_screen(self, level_num: int) -> Screen:
        """Create a new instance of GamePaused screen"""

    @abstractmethod
    def get_level_completed_screen(self, level_score: LevelScore) -> Screen:
        """Create a new instance of LevelCompleted screen"""

    @abstractmethod
    def get_tutorial_screen(self) -> Screen:
        """Create a new instance of Tutorial screen"""

    @abstractmethod
    def get_victory_screen(self) -> Screen:
        """Create a new instance of VictoryCompleted screen"""

    @abstractmethod
    def get_exit_screen(self, exit_callback: Callable) -> Screen:
        """Create a new instance of Exit screen"""
