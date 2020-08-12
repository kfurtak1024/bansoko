"""
Module containing level related classes.
"""
from typing import NamedTuple, List

import pyxel

from game.tiles import TilePosition, TileSet

NUM_LEVELS: int = 60
LEVEL_SIZE = 32
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


class LevelTemplate:
    level_num: int
    tiles: TileSet
    player_pos: TilePosition
    crates_pos: List[TilePosition]

    def __init__(self, level_num: int):
        self.level_num = level_num
        # TODO: Hard-coded! Should be taken from resources!
        self.tiles = TileSet([{}, {}, {2, 9, 16, 23, 30}, {}, {4, 11, 18, 25, 32}, {5, 12, 19, 26, 33}, {}])
        self.crates_pos = []
        tile_map = pyxel.tilemap(0)
        tile_map_u = self.tile_map_u
        tile_map_v = self.tile_map_v
        for u in range(tile_map_u, tile_map_u + LEVEL_SIZE):
            for v in range(tile_map_v, tile_map_v + LEVEL_SIZE):
                tile = tile_map.get(u, v)
                position = TilePosition(u - tile_map_u, v - tile_map_v)
                if self.tiles.is_crate(tile):
                    self.crates_pos.append(position)
                elif self.tiles.is_player_start(tile):
                    self.player_pos = position

    @property
    def tile_map_u(self) -> int:
        return LEVEL_SIZE * (self.level_num % TILE_SIZE)

    @property
    def tile_map_v(self) -> int:
        return LEVEL_SIZE * (self.level_num // TILE_SIZE)
