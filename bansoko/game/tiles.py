"""Module exposing tile-related types."""
from enum import Enum, unique, auto


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


class Tileset:
    def __init__(self, tileset_index: int) -> None:
        self.first_tile_index = tileset_index * len(TileType)
        self.tile_indexes = list(TileType)

    def tile_of(self, tile_index: int) -> TileType:
        num_tiles = len(TileType)
        index_in_range = self.first_tile_index <= tile_index < self.first_tile_index + num_tiles
        return self.tile_indexes[tile_index % num_tiles] if index_in_range else TileType.VOID
