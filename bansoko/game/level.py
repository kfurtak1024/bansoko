"""
Module containing level related classes.
"""
from enum import Enum, unique
from typing import NamedTuple

import pyxel

NUM_LEVELS: int = 60
LEVEL_SIZE = 32
TILE_SIZE = 8


@unique
class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class LevelStatistics(NamedTuple):
    """
    Player's score for given level.

    Attributes:
        level_num - level number (value from 0 to NUM_LEVELS-1)
        moves - number of moves that player made
                ("move" happens when player pushes a crate)
        steps - number of steps that player made
                ("step" happens when player moves by one cell in any direction)
        time - time spent playing the level
    """

    level_num: int
    moves: int = 0
    steps: int = 0
    time: int = 0


class Level:
    def __init__(self, level_num: int):
        self.statistics = LevelStatistics(level_num)

    def is_completed(self) -> bool:
        # TODO: Not implemented yet!
        return False

    def move_player(self, direction: Direction) -> None:
        if direction is Direction.UP:
            # TODO: Not implemented yet!
            pass
        elif direction is Direction.DOWN:
            # TODO: Not implemented yet!
            pass
        elif direction is Direction.LEFT:
            # TODO: Not implemented yet!
            pass
        elif direction is Direction.RIGHT:
            # TODO: Not implemented yet!
            pass

    def update(self):
        # TODO: Not implemented yet!
        pass

    def draw(self):
        level_num = self.statistics.level_num
        tile_map_u = LEVEL_SIZE * (level_num % TILE_SIZE)
        tile_map_v = LEVEL_SIZE * (level_num // TILE_SIZE)
        pyxel.bltm(0, 0, 0, tile_map_u, tile_map_v, LEVEL_SIZE, LEVEL_SIZE)
