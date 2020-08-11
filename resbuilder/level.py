from typing import Dict

from tiles import Tile


class LevelTheme:
    tiles_ids: Dict[Tile, int]

    def __init__(self, tiles_ids: Dict[Tile, int], thumbnail_colors: Dict[Tile, int]):
        self.tiles_ids = tiles_ids
        self.thumbnail_colors = thumbnail_colors

    def tile_id(self, tile: Tile) -> int:
        return self.tiles_ids[tile]

    def thumbnail_color(self, tile: Tile) -> int:
        return self.thumbnail_colors[tile]
