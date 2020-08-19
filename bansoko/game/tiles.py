"""Module exposing tile-related types."""
from enum import Enum, unique
from typing import NamedTuple, Dict, Any

import pyxel

from bansoko.graphics import Point

# TODO: Should be taken from bundle
LEVEL_WIDTH = 32
LEVEL_HEIGHT = 32
TILE_SIZE = 8


@unique
class TileType(Enum):
    VOID = 0, "tile_void"
    WALL = 1, "tile_wall"
    PLAYER_START = 2, "tile_player_start"
    FLOOR = 3, "tile_floor"
    INITIAL_CRATE_POSITION = 4, "tile_initial_crate_position"
    CRATE_INITIALLY_PLACED = 5, "tile_crate_initially_placed"
    CARGO_BAY = 6, "tile_cargo_bay"

    def __init__(self, tile_index: int, tile_name: str) -> None:
        self.tile_index = tile_index
        self.tile_name = tile_name

    @property
    def is_player_start(self) -> bool:
        return self == TileType.PLAYER_START

    @property
    def is_cargo_bay(self) -> bool:
        return self == TileType.CARGO_BAY

    @property
    def is_crate_spawn_point(self) -> bool:
        return self in (TileType.INITIAL_CRATE_POSITION, TileType.CRATE_INITIALLY_PLACED)

    @property
    def is_walkable(self) -> bool:
        return self in (TileType.PLAYER_START, TileType.FLOOR, TileType.INITIAL_CRATE_POSITION,
                        TileType.CRATE_INITIALLY_PLACED, TileType.CARGO_BAY)


@unique
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def __init__(self, dx: int, dy: int) -> None:
        self.dx = dx
        self.dy = dy


class TilePosition(NamedTuple):
    tile_x: int = 0
    tile_y: int = 0

    def move(self, direction: Direction) -> "TilePosition":
        return TilePosition(self.tile_x + direction.dx, self.tile_y + direction.dy)

    def to_point(self) -> Point:
        return Point(self.tile_x * TILE_SIZE, self.tile_y * TILE_SIZE)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TilePosition):
            return self.tile_x == other.tile_x and self.tile_y == other.tile_y
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.tile_x, self.tile_y))


class Tileset:
    def __init__(self, tiles_dict: Dict[str, int]) -> None:
        self.tiles = [tiles_dict[tile.tile_name] for tile in list(TileType)]  # TODO: Not needed anymore
        self.index_to_tile = {self.tiles[tile.tile_index]: tile for tile in list(TileType)}

    def tile_of(self, tile_index: int) -> TileType:
        if self.index_to_tile.get(tile_index) is None:
            # TODO: VOID should be unique per tileset, so we never reach this place
            return TileType.VOID
        return self.index_to_tile[tile_index]


class Tilemap:
    def __init__(self, tileset: Tileset, u: int, v: int) -> None:
        self.tilemap = pyxel.tilemap(0)
        self.tileset = tileset
        self.u = u
        self.v = v

        crates_list = []

        for y in range(LEVEL_HEIGHT):
            for x in range(LEVEL_WIDTH):
                tile_pos = TilePosition(x, y)
                tile = self.tile_at(tile_pos)
                if tile.is_crate_spawn_point:
                    crates_list.append(tile_pos)
                elif tile.is_player_start:
                    self.player_start = tile_pos

        self.crates = tuple(crates_list)

    def tile_at(self, position: TilePosition) -> TileType:
        tile_index = self.tilemap.get(self.u + position.tile_x, self.v + position.tile_y)
        return self.tileset.tile_of(tile_index)
