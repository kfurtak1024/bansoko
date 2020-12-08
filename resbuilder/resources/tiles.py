"""Module exposing tiles related utilities (like Tile and TilePacker)"""
from enum import unique, Enum
from pathlib import Path
from typing import Dict

import pyxel

from bansoko import LEVEL_WIDTH, LEVEL_HEIGHT
from bansoko.graphics import Rect, IMAGE_BANK_WIDTH, TILE_SIZE, TILEMAP_WIDTH


@unique
class Tile(Enum):
    """Game-logic specific tiles used during parsing levels from input resource file."""
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
    """Packer for packing tiles into a single Pyxel's image bank.

    Attributes:
        image_bank - Pyxel's image bank to pack tiles into
        base_dir - the base directory of all tiles images
        next_free_tile - tile id that will be assigned to a tile during next call to pack_tile()
    """

    def __init__(self, image_bank: int, base_dir: Path) -> None:
        self.image_bank = image_bank
        self.base_dir = base_dir
        self.next_free_tile = 0

    def pack_tileset(self, theme_data: Dict[str, str]) -> Dict[Tile, int]:
        """Pack a whole tileset into Pyxel's image bank this TilePacker controls.

        :param theme_data: data from JSON file describing tileset
        :return: packed tileset
        """
        level_theme: Dict[Tile, int] = {}
        for tile in list(Tile):
            if theme_data.get(tile.tile_name):
                level_theme[tile] = self.pack_tile(theme_data[tile.tile_name])
        return level_theme

    def pack_tile(self, filename: str) -> int:
        """Pack a single tile into Pyxel's image bank this TilePacker controls.

        :param filename: filename of tile image
        :return: the id of the tile (which can be used in a tilemap)
        """
        tiles_in_row = IMAGE_BANK_WIDTH // TILE_SIZE
        x = (self.next_free_tile % tiles_in_row) * TILE_SIZE
        y = (self.next_free_tile // tiles_in_row) * TILE_SIZE
        pyxel.image(self.image_bank).load(x, y, Path(self.base_dir).joinpath(filename))
        self.next_free_tile = self.next_free_tile + 1
        return self.next_free_tile - 1


def tilemap_rect_nth(index: int) -> Rect:
    """Create a rectangle representing position and size of n-th tilemap in Pyxel's mega-tilemap.

    :param index: index of tilemap to create rectangle for
    :return: tilemap's rect (representing position and size of a tilemap expressed in tiles)
    """
    levels_horizontally = TILEMAP_WIDTH // LEVEL_WIDTH
    return Rect.from_coords(
        (index % levels_horizontally) * LEVEL_WIDTH,
        (index // levels_horizontally) * LEVEL_HEIGHT,
        LEVEL_WIDTH, LEVEL_HEIGHT)
