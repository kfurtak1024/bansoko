"""Module containing level related classes."""
from typing import NamedTuple, List

import pyxel

from bansoko.game.tiles import TilePosition, TileSet
from bansoko.graphics.sprite import Sprite

NUM_LEVELS: int = 60

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


class LevelTemplate:
    level_num: int
    tiles: TileSet
    # TODO: Add LevelSprites
    player_pos: TilePosition
    crates_pos: List[TilePosition]

    def __init__(self, level_num: int, tiles: TileSet):
        self.level_num = level_num
        self.tiles = tiles
        self.crates_pos = []
        tile_map = pyxel.tilemap(0)
        tile_map_u = self.tile_map_u
        tile_map_v = self.tile_map_v
        for u in range(tile_map_u, tile_map_u + LEVEL_WIDTH):
            for v in range(tile_map_v, tile_map_v + LEVEL_HEIGHT):
                tile = tile_map.get(u, v)
                position = TilePosition(u - tile_map_u, v - tile_map_v)
                if self.tiles.is_crate(tile):
                    self.crates_pos.append(position)
                elif self.tiles.is_player_start(tile):
                    self.player_pos = position

    # TODO: Consider adding fromJson()

    @property
    def tile_map_u(self) -> int:
        return LEVEL_WIDTH * (self.level_num % TILE_SIZE)

    @property
    def tile_map_v(self) -> int:
        return LEVEL_HEIGHT * (self.level_num // TILE_SIZE)
