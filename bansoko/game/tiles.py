"""Module exposing tile-related types."""
from enum import Enum, unique, auto
from typing import NamedTuple, Any

import pyxel

from bansoko.graphics import Point

# TODO: Should be taken from bundle
LEVEL_WIDTH = 32
LEVEL_HEIGHT = 32
TILE_SIZE = 8


@unique
class TileType(Enum):
    VOID = auto()
    WALL = auto()
    PLAYER_START = auto()
    FLOOR = auto()
    INITIAL_CRATE_POSITION = auto()
    CRATE_INITIALLY_PLACED = auto()
    CARGO_BAY = auto()

    @property
    def is_player_start(self) -> bool:
        return self == TileType.PLAYER_START

    @property
    def is_crate_initially_placed(self) -> bool:
        return self == TileType.CRATE_INITIALLY_PLACED

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
    # TODO: Hard-coded 7
    def __init__(self, theme_index: int) -> None:
        self.first_tile_index = theme_index * 7
        self.tile_indexes = [tile for tile in list(TileType)]

    def tile_of(self, tile_index: int) -> TileType:
        num_tiles = 7
        index_in_range = self.first_tile_index <= tile_index < self.first_tile_index + num_tiles
        return self.tile_indexes[tile_index % num_tiles] if index_in_range else TileType.VOID


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
