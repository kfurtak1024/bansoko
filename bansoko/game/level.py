"""
Module containing level related classes.
"""
from typing import NamedTuple

NUM_LEVELS = 60


class LevelStatistics(NamedTuple):
    """
    Player's score for given level.

    Attributes:
        level - level number (value from 0 to NUM_LEVELS-1)
        moves - number of moves that player made
                ("move" happens when player pushes a crate)
        steps - number of steps that player made
                ("step" happens when player moves by one cell in any direction)
        time - time spent playing the level
    """

    level: int
    moves: int = 0
    steps: int = 0
    time: int = 0
