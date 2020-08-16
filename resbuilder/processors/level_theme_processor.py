from typing import Dict, List

from processors.tile_processor import Tile, TileSetPacker


class LevelTheme:
    tile_void_id: int
    tiles_ids: List[Dict[Tile, int]]

    def __init__(self, tile_void_id: int, tiles_ids: List[Dict[Tile, int]],
                 thumbnail_colors: Dict[Tile, int]):
        self.tile_void_id = tile_void_id
        self.tiles_ids = tiles_ids
        self.thumbnail_colors = thumbnail_colors

    @property
    def num_layers(self):
        return len(self.tiles_ids)

    def tile_id(self, layer: int, tile: Tile) -> int:
        return self.tiles_ids[layer].get(tile, self.tile_void_id)

    def thumbnail_color(self, tile: Tile) -> int:
        return self.thumbnail_colors[tile]


def generate_level_themes(base_dir: str, data) -> List[LevelTheme]:
    packer = TileSetPacker(data["tiles_image_bank"], base_dir)
    themes: List[LevelTheme] = []

    for level_theme_data in data["themes"]:
        tile_void = packer.pack_tile(level_theme_data["tiles"]["tile_void"])
        layers = []
        for tiles_layers in level_theme_data["tiles"]["layers"]:
            layers.append(packer.pack_level_theme(tiles_layers))

        themes.append(LevelTheme(
            tile_void,
            layers,
            _extract_thumbnail_colors(level_theme_data["thumbnail"])
        ))

    return themes


def _extract_thumbnail_colors(data) -> Dict[Tile, int]:
    thumbnail_colors: Dict[Tile, int] = {}

    for tile in list(Tile):
        thumbnail_colors[tile] = data[tile.thumbnail_color_name]

    return thumbnail_colors
