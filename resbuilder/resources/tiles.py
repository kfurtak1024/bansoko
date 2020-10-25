from enum import unique, Enum
from pathlib import Path
from typing import Dict

import pyxel

IMAGE_BANK_SIZE = 256
TILE_SIZE = 8


@unique
class Tile(Enum):
    VOID = ("tile_void", " ")
    WALL = ("tile_wall", "X")
    START = ("tile_start", "@")
    FLOOR = ("tile_floor", ".")
    INITIAL_CRATE_POSITION = ("tile_initial_crate_position", "#")
    CRATE_INITIALLY_PLACED = ("tile_crate_initially_placed", "&")
    CARGO_BAY = ("tile_cargo_bay", "+")

    def __init__(self, tile_name: str, tile_symbol: str):
        self.tile_name = tile_name
        self.tile_symbol = tile_symbol


SYMBOL_TO_TILE = {tile.tile_symbol: tile for tile in list(Tile)}


class TilePacker:
    def __init__(self, image_bank: int, base_dir: Path) -> None:
        self.image_bank = image_bank
        self.base_dir = base_dir
        self.next_free_tile = 0

    def pack_tileset(self, theme_data: Dict[str, str]) -> Dict[Tile, int]:
        level_theme: Dict[Tile, int] = {}
        for tile in list(Tile):
            if theme_data.get(tile.tile_name):
                level_theme[tile] = self.pack_tile(theme_data[tile.tile_name])
        return level_theme

    def pack_tile(self, filename: str) -> int:
        tiles_in_row = IMAGE_BANK_SIZE / TILE_SIZE
        x = (self.next_free_tile % tiles_in_row) * TILE_SIZE
        y = (self.next_free_tile // tiles_in_row) * TILE_SIZE
        pyxel.image(self.image_bank).load(x, y, Path(self.base_dir).joinpath(filename))
        self.next_free_tile = self.next_free_tile + 1
        return self.next_free_tile - 1
