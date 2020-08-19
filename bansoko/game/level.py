"""Module containing level related classes."""
from enum import Enum, unique
from typing import NamedTuple, Tuple

import pyxel

from bansoko.game.tiles import TilePosition, TileSet
from bansoko.graphics import Point
from bansoko.graphics.sprite import Sprite


# TODO: Should be taken from bundle
LEVEL_WIDTH = 32
LEVEL_HEIGHT = 32
TILE_SIZE = 8


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

    @classmethod
    def num_layers(cls) -> int:
        return len(cls.__members__)

    @property
    def is_main(self) -> bool:
        return self == LevelLayer.MAIN_LAYER


class LevelTemplate:
    level_num: int
    tiles: TileSet
    # TODO: Add LevelSprites
    player_pos: TilePosition
    crates_pos: Tuple[TilePosition, ...]

    def __init__(self, level_num: int, tiles: TileSet):
        self.level_num = level_num
        self.tiles = tiles
        crates_pos_list = []
        tile_map = pyxel.tilemap(0)
        tile_map_u = self.tile_map_u
        tile_map_v = self.tile_map_v
        for u in range(tile_map_u, tile_map_u + LEVEL_WIDTH):
            for v in range(tile_map_v, tile_map_v + LEVEL_HEIGHT):
                tile = tile_map.get(u, v)
                position = TilePosition(u - tile_map_u, v - tile_map_v)
                if self.tiles.is_crate(tile):
                    crates_pos_list.append(position)
                elif self.tiles.is_player_start(tile):
                    self.player_pos = position
        self.crates_pos = tuple(crates_pos_list)

    # TODO: Consider adding fromJson()

    @property
    def tile_map_u(self) -> int:
        return LEVEL_WIDTH * (self.level_num % TILE_SIZE)

    @property
    def tile_map_v(self) -> int:
        return LEVEL_HEIGHT * (self.level_num // TILE_SIZE)
