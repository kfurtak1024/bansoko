from pathlib import Path
from typing import Dict, List

from resbuilder.processors.tile_processor import Tile, TilesetPacker


class LevelTheme:
    tiles_ids: List[Dict[Tile, int]]

    def __init__(self, tiles_ids: List[Dict[Tile, int]], thumbnail_colors: Dict[Tile, int]):
        self.tiles_ids = tiles_ids
        self.thumbnail_colors = thumbnail_colors

    @property
    def num_layers(self) -> int:
        return len(self.tiles_ids)

    def tile_id(self, layer: int, tile: Tile) -> int:
        return self.tiles_ids[layer].get(tile, self.tiles_ids[0][Tile.VOID])

    def thumbnail_color(self, tile: Tile) -> int:
        return self.thumbnail_colors[tile]


def generate_level_themes(base_dir: Path, data) -> List[LevelTheme]:
    # TODO: Refactor it
    packer = TilesetPacker(data["tiles_image_bank"], base_dir)
    themes: List[LevelTheme] = []

    main_layers: List[Dict[Tile, int]] = []

    for level_theme_data in data["themes"]:
        main_layers.append(packer.pack_level_theme(level_theme_data["tiles"]["layers"][0]))

    for i, level_theme_data in enumerate(data["themes"]):
        layers = [main_layers[i]]
        for j in range(1, 3):
            layers.append(packer.pack_level_theme(level_theme_data["tiles"]["layers"][j]))

        themes.append(LevelTheme(
            layers, _extract_thumbnail_colors(level_theme_data["thumbnail_colors"])))

    return themes


def _extract_tiles(level_theme: LevelTheme):
    # TODO: Hard-coded 0
    return {tile.tile_name: level_theme.tile_id(0, tile) for tile in list(Tile)}


def _extract_thumbnail_colors(data) -> Dict[Tile, int]:
    thumbnail_colors: Dict[Tile, int] = {}

    for tile in list(Tile):
        thumbnail_colors[tile] = data[tile.tile_name]

    return thumbnail_colors
