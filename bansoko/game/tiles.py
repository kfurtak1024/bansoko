"""Module exposing tile-related types."""
from enum import Enum, unique
from typing import NamedTuple, Dict


@unique
class TileType(Enum):
    VOID = 0, "tile_void"
    WALL = 1, "tile_wall"
    PLAYER_START = 2, "tile_player_start"
    FLOOR = 3, "tile_floor"
    INITIAL_CRATE_POSITION = 4, "tile_initial_crate_position"
    CRATE_INITIALLY_PLACED = 5, "tile_crate_initially_placed"
    CARGO_BAY = 6, "tile_cargo_bay"

    def __init__(self, tile_index, tile_name):
        self.tile_index = tile_index
        self.tile_name = tile_name


class TileSet:
    def __init__(self, tiles_dict: Dict[str, int]):
        self.tiles = [tiles_dict[tile.tile_name] for tile in list(TileType)]

    def is_void(self, tile: int) -> bool:
        return tile == self.tiles[TileType.VOID.tile_index]

    def is_wall(self, tile: int) -> bool:
        return tile == self.tiles[TileType.WALL.tile_index]

    def is_player_start(self, tile: int) -> bool:
        return tile == self.tiles[TileType.PLAYER_START.tile_index]

    def is_floor(self, tile: int) -> bool:
        return tile == self.tiles[TileType.FLOOR.tile_index]

    def is_initial_crate_position(self, tile: int) -> bool:
        return tile == self.tiles[TileType.INITIAL_CRATE_POSITION.tile_index]

    def is_crate_initially_placed(self, tile: int) -> bool:
        return tile == self.tiles[TileType.CRATE_INITIALLY_PLACED.tile_index]

    def is_cargo_bay(self, tile: int) -> bool:
        return tile == self.tiles[TileType.CARGO_BAY.tile_index]

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
