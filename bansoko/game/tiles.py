from enum import Enum, unique, IntEnum
from typing import NamedTuple, Set, List


@unique
class TileType(IntEnum):
    VOID = "tile_void"
    WALL = "tile_wall"
    PLAYER_START = "tile_player_start"
    FLOOR = "tile_floor"
    INITIAL_CRATE_POSITION = "tile_initial_crate_position"
    CRATE_INITIALLY_PLACED = "tile_crate_initially_placed"
    CARGO_BAY = "tile_cargo_bay"

    def __new__(cls, tile_name: str):
        value = len(cls.__members__)
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.tile_name = tile_name
        return obj


class TileSet:
    tiles: List[Set[int]]

    def __init__(self, tiles: List[Set[int]]):
        self.tiles = tiles

    def is_void(self, tile: int) -> bool:
        return tile in self.tiles[TileType.VOID]

    def is_wall(self, tile: int) -> bool:
        return tile in self.tiles[TileType.WALL]

    def is_player_start(self, tile: int) -> bool:
        return tile in self.tiles[TileType.PLAYER_START]

    def is_floor(self, tile: int) -> bool:
        return tile in self.tiles[TileType.FLOOR]

    def is_initial_crate_position(self, tile: int) -> bool:
        return tile in self.tiles[TileType.INITIAL_CRATE_POSITION]

    def is_crate_initially_placed(self, tile: int) -> bool:
        return tile in self.tiles[TileType.CRATE_INITIALLY_PLACED]

    def is_cargo_bay(self, tile: int) -> bool:
        return tile in self.tiles[TileType.CARGO_BAY]

    def is_crate(self, tile: int) -> bool:
        return self.is_crate_initially_placed(tile) or self.is_initial_crate_position(tile)


@unique
class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class TilePosition(NamedTuple):
    tile_x: int = 0
    tile_y: int = 0

    def move(self, direction: Direction):
        destination_x = self.tile_x
        destination_y = self.tile_y
        # TODO: Can I move it to Direction enum?
        if direction is Direction.UP:
            destination_y -= 1
        elif direction is Direction.DOWN:
            destination_y += 1
        elif direction is Direction.LEFT:
            destination_x -= 1
        elif direction is Direction.RIGHT:
            destination_x += 1
        return TilePosition(destination_x, destination_y)