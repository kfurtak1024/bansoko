from typing import Dict, List

from resbuilder.processors.tile_processor import Tile, TilesetPacker


class LevelTheme:
    tile_void_id: int
    tiles_ids: List[Dict[Tile, int]]

    def __init__(self, tile_void_id: int, tiles_ids: List[Dict[Tile, int]],
                 thumbnail_colors: Dict[Tile, int]):
        self.tile_void_id = tile_void_id
        self.tiles_ids = tiles_ids
        self.thumbnail_colors = thumbnail_colors

    @property
    def num_layers(self) -> int:
        return len(self.tiles_ids)

    def tile_id(self, layer: int, tile: Tile) -> int:
        return self.tiles_ids[layer].get(tile, self.tile_void_id)

    def thumbnail_color(self, tile: Tile) -> int:
        return self.thumbnail_colors[tile]


def generate_level_themes(base_dir: str, data) -> List[LevelTheme]:
    packer = TilesetPacker(data["tiles_image_bank"], base_dir)
    themes: List[LevelTheme] = []

    for level_theme_data in data["themes"]:
        tile_void = packer.pack_tile(level_theme_data["tiles"]["tile_void"])
        layers = []
        for tiles_layers in level_theme_data["tiles"]["layers"]:
            layers.append(packer.pack_level_theme(tiles_layers))

        themes.append(LevelTheme(
            tile_void,
            layers,
            _extract_thumbnail_colors(level_theme_data["thumbnail_colors"])
        ))

    return themes


def process_level_themes(level_themes: List[LevelTheme]):
    return [{"tiles": _extract_tiles(level_theme)} for level_theme in level_themes]


def _extract_tiles(level_theme: LevelTheme):
    # TODO: Hard-coded 0
    return {tile.tile_name: level_theme.tile_id(0, tile) for tile in list(Tile)}


def _extract_thumbnail_colors(data) -> Dict[Tile, int]:
    thumbnail_colors: Dict[Tile, int] = {}

    for tile in list(Tile):
        thumbnail_colors[tile] = data[tile.tile_name]

    return thumbnail_colors
