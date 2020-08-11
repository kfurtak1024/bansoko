from enum import Enum, unique
from typing import NamedTuple


@unique
class Tile(Enum):
    VOID = 0, "tile_void"
    WALL = 1, "tile_wall"
    PLAYER_START = 2, "tile_player_start"
    FLOOR = 3, "tile_floor"
    INITIAL_CRATE_POSITION = 4, "tile_crate"
    CRATE_INITIALLY_PLACED = 5, "tile_crate_placed"
    CARGO_BAY = 6, "tile_cargo_bay"

    def __new__(cls, keycode: int, tile_name: str):
        obj = object.__new__(cls)
        obj._value_ = keycode
        obj.tile_name = tile_name
        return obj


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