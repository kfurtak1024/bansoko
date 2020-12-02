"""Module providing an abstraction over screen controllers creation."""
from abc import ABC, abstractmethod
from typing import Callable

from bansoko.game.bundle import Bundle
from bansoko.game.profile import PlayerProfile, LevelScore
from bansoko.gui.navigator import ScreenController


class ScreenFactory(ABC):
    """An abstraction over screen controllers creation.

    By having this abstraction we're solving the problem with circular dependencies between screen
    controllers.
    """

    @abstractmethod
    def get_bundle(self) -> Bundle:
        """..."""

    @abstractmethod
    def get_player_profile(self) -> PlayerProfile:
        """..."""

    @abstractmethod
    def get_main_menu(self) -> ScreenController:
        """Create a new instance of Main Menu screen controller"""

    @abstractmethod
    def get_playfield_screen(self, level_num: int,
                             skip_how_to_play: bool = False) -> ScreenController:
        """Create a new instance of Playfield screen controller"""

    @abstractmethod
    def get_choose_level_screen(self) -> ScreenController:
        """Create a new instance of Choose Level screen controller"""

    @abstractmethod
    def get_game_paused_screen(self, level_num: int) -> ScreenController:
        """Create a new instance of Game Paused screen controller"""

    @abstractmethod
    def get_level_completed_screen(self, level_score: LevelScore) -> ScreenController:
        """Create a new instance of Level Completed screen controller"""

    @abstractmethod
    def get_how_to_play_screen(self) -> ScreenController:
        """Create a new instance of How To Play screen controller"""

    @abstractmethod
    def get_victory_screen(self) -> ScreenController:
        """Create a new instance of Victory Completed screen controller"""

    @abstractmethod
    def get_exit_screen(self, exit_callback: Callable[[], None]) -> ScreenController:
        """Create a new instance of Exit screen controller"""
