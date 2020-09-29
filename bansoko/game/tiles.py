"""Module exposing tile-related types."""
from enum import Enum, unique, auto
from typing import NamedTuple, Any, Generator

import pyxel

from bansoko.graphics import Point, Direction, Rect, Layer

# TODO: Should be taken from bundle
LEVEL_WIDTH = 32
LEVEL_HEIGHT = 32
TILE_SIZE = 8


@unique
class TileType(Enum):
    VOID = auto()
    WALL = auto()
    START = auto()
    FLOOR = auto()
    INITIAL_CRATE_POSITION = auto()
    CRATE_INITIALLY_PLACED = auto()
    CARGO_BAY = auto()

    @property
    def is_start(self) -> bool:
        return self == TileType.START

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
        return self in (TileType.START, TileType.FLOOR, TileType.INITIAL_CRATE_POSITION,
                        TileType.CRATE_INITIALLY_PLACED, TileType.CARGO_BAY)


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
    def __init__(self, tileset_index: int) -> None:
        self.first_tile_index = tileset_index * len(TileType)
        self.tile_indexes = list(TileType)

    def tile_of(self, tile_index: int) -> TileType:
        num_tiles = len(TileType)
        index_in_range = self.first_tile_index <= tile_index < self.first_tile_index + num_tiles
        return self.tile_indexes[tile_index % num_tiles] if index_in_range else TileType.VOID


class Tilemap(NamedTuple):
    tilemap_id: int
    rect_uv: Rect
    num_layers: int = 1

    @property
    def width(self) -> int:
        return self.rect_uv.w

    @property
    def height(self) -> int:
        return self.rect_uv.h

    def tile_index_at(self, position: TilePosition) -> int:
        tile_index: int = pyxel.tilemap(self.tilemap_id).get(
            self.rect_uv.x + position.tile_x, self.rect_uv.y + position.tile_y)
        return tile_index

    def draw(self, layer: Layer) -> None:
        if layer and layer.layer_index >= self.num_layers:
            return

        pyxel.bltm(layer.offset.x, layer.offset.y, self.tilemap_id + layer.layer_index,
                   self.rect_uv.x, self.rect_uv.y, self.rect_uv.w, self.rect_uv.h,
                   colkey=-1 if layer.layer_index == 0 else 0)  # TODO: Layer should have information about transparent color!

    def tiles_positions(self) -> Generator[TilePosition, None, None]:
        for i in range(self.width * self.height):
            yield TilePosition(i % self.width, i // self.width)
