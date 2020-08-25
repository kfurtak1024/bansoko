"""Module containing level related classes."""
from enum import Enum, unique
from typing import NamedTuple

from bansoko.game.tiles import Tileset, Tilemap, LEVEL_WIDTH, LEVEL_HEIGHT, TILE_SIZE
from bansoko.graphics import Point
from bansoko.graphics.sprite import Sprite


class LevelStatistics:
    """
    Player's score for given level.

    Attributes:
        level_num - level number (value from 0 to NUM_LEVELS-1)
        pushes - number of moves that player made
                 ("move" happens when player pushes a crate)
        steps - number of steps that player made
                ("step" happens when player moves by one cell in any direction)
        time_in_ms - time spent playing the level (expressed in milliseconds)
    """

    def __init__(self, level_num: int):
        self.level_num: int = level_num
        self.pushes: int = 0
        self.steps: int = 0
        self.time_in_ms: int = 0


class LevelSprites(NamedTuple):
    crate: Sprite
    crate_placed: Sprite


@unique
class LevelLayer(Enum):
    MAIN_LAYER = 0, Point(0, 0)
    LAYER_1 = 1, Point(-1, -1)
    LAYER_2 = 2, Point(-2, -2)

    def __init__(self, layer_index: int, offset: Point):
        self.layer_index = layer_index
        self.offset = offset

    @property
    def is_main(self) -> bool:
        return self == LevelLayer.MAIN_LAYER


# TODO: Is it needed in this form?
class LevelTemplate:
    level_num: int
    tilemap: Tilemap
    # TODO: Add LevelSprites?

    def __init__(self, level_num: int, theme_index: int):
        tilemap_u = LEVEL_WIDTH * (level_num % TILE_SIZE)
        tilemap_v = LEVEL_HEIGHT * (level_num // TILE_SIZE)
        self.level_num = level_num
        self.tilemap = Tilemap(Tileset(theme_index), tilemap_u, tilemap_v)
