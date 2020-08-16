from enum import unique, Enum
from pathlib import Path
from typing import Dict

import pyxel

IMAGE_BANK_SIZE = 256
TILE_SIZE = 8


@unique
class Tile(Enum):
    VOID = 0, "tile_void", "color_void"
    WALL = 1, "tile_wall", "color_wall"
    PLAYER_START = 2, "tile_player_start", "color_player_start"
    FLOOR = 3, "tile_floor", "color_floor"
    INITIAL_CRATE_POSITION = 4, "tile_initial_crate_position", "color_initial_crate_position"
    CRATE_INITIALLY_PLACED = 5, "tile_crate_initially_placed", "color_crate_initially_placed"
    CARGO_BAY = 6, "tile_cargo_bay", "color_cargo_bay"

    def __new__(cls, keycode: int, theme_tile_name: str, thumbnail_color_name):
        obj = object.__new__(cls)
        obj._value_ = keycode
        obj.theme_item_name = theme_tile_name
        obj.thumbnail_color_name = thumbnail_color_name
        return obj


class TileSetPacker:
    def __init__(self, image_bank: int, base_dir: str):
        self.image_bank = image_bank
        self.base_dir = base_dir
        self.next_free_tile = 0

    def pack_level_theme(self, theme_data) -> Dict[Tile, int]:
        tiles_ids: Dict[Tile, int] = {}

        for tile in list(Tile):
            if theme_data.get(tile.theme_item_name) is not None:
                tiles_ids[tile] = self.pack_tile(theme_data[tile.theme_item_name])

        return tiles_ids

    def pack_tile(self, filename: str) -> int:
        tiles_in_row = IMAGE_BANK_SIZE / TILE_SIZE
        x = (self.next_free_tile % tiles_in_row) * TILE_SIZE
        y = (self.next_free_tile // tiles_in_row) * TILE_SIZE
        pyxel.image(self.image_bank).load(x, y, Path(self.base_dir).joinpath(filename))
        self.next_free_tile = self.next_free_tile + 1
        return self.next_free_tile - 1
