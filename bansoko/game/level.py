"""
Module containing level related classes.
"""
from typing import NamedTuple, List

import pyxel

from game.tiles import Tile, TilePosition

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


class LevelTiles:
    def __init__(self, level_num: int):
        # TODO: Not implemented yet!
        pass

    def tile_id(self, tile: Tile) -> int:
        # TODO: Not implemented yet!
        return 0

    def tile(self, id: int) -> Tile:
        # TODO: Not implemented yet!
        return Tile.WALL


class LevelTemplate:
    level_num: int
    level_tiles: LevelTiles
    player_pos: TilePosition
    crates_pos: List[TilePosition]

    def __init__(self, level_num: int):
        self.level_num = level_num
        self.level_tiles = LevelTiles(level_num)
        self.crates_pos = []
        tile_map = pyxel.tilemap(0)
        tile_map_u = self.tile_map_u
        tile_map_v = self.tile_map_v
        for u in range(tile_map_u, tile_map_u + LEVEL_SIZE):
            for v in range(tile_map_v, tile_map_v + LEVEL_SIZE):
                tile = tile_map.get(u, v)
                position = TilePosition(u - tile_map_u, v - tile_map_v)
                if self.__is_crate_tile(tile):
                    self.crates_pos.append(position)
                elif self.__is_player_start_tile(tile):
                    self.player_pos = position

    @property
    def tile_map_u(self) -> int:
        return LEVEL_SIZE * (self.level_num % TILE_SIZE)

    @property
    def tile_map_v(self) -> int:
        return LEVEL_SIZE * (self.level_num // TILE_SIZE)

    def __is_crate_tile(self, tile_id: int) -> bool:
        #tile = self.level_tiles.tile(tile_id)
        #return tile == Tile.INITIAL_CRATE_POSITION or tile == Tile.CRATE_INITIALLY_PLACED
        # TODO: Read it from resources file (instead of hard-coded values)
        return tile_id in [4, 5, 11, 12, 18, 19, 25, 26, 32, 33]

    def __is_player_start_tile(self, tile_id: int) -> bool:
        #tile = self.level_tiles.tile(tile_id)
        #return tile == Tile.PLAYER_START
        # TODO: Read it from resources file (instead of hard-coded values)
        return tile_id in [2, 9, 16, 23, 30]
