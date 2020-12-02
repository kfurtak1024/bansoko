"""Module for game globals."""


class GameError(Exception):
    """Base class for exceptions in Bansoko."""

    def __init__(self, message: str):
        super().__init__()
        self.message = message
