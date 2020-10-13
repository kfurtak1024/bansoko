from dataclasses import dataclass
from typing import Dict, List, Any

from resbuilder.resources.tiles import Tile, TilePacker


@dataclass(frozen=True)
class LevelTheme:
    tiles_ids: List[Dict[Tile, int]]
    background_generator: str
    thumbnail_colors: Dict[Tile, int]
    robot_sprite_pack: str
    crate_sprite_pack: str

    @property
    def num_layers(self) -> int:
        return len(self.tiles_ids)

    def tile_id(self, layer: int, tile: Tile) -> int:
        return self.tiles_ids[layer].get(tile, self.tiles_ids[0][Tile.VOID])

    def thumbnail_color(self, tile: Tile) -> int:
        return self.thumbnail_colors[tile]


def generate_level_themes(data: Any, tile_packer: TilePacker, sprite_packs: Dict[str, Any]) \
        -> List[LevelTheme]:
    # TODO: Refactor it
    themes: List[LevelTheme] = []

    main_layers: List[Dict[Tile, int]] = []

    for level_theme_data in data:
        main_layers.append(tile_packer.pack_level_theme(level_theme_data["tiles"]["layers"][0]))

    for i, level_theme_data in enumerate(data):
        layers = [main_layers[i]]
        for j in range(1, 3):
            layers.append(tile_packer.pack_level_theme(level_theme_data["tiles"]["layers"][j]))

        background_generator = level_theme_data["background_generator"]
        thumbnail_colors = _extract_thumbnail_colors(level_theme_data["thumbnail_colors"])
        robot_sprite_pack = level_theme_data["sprite_packs"]["robot"]
        if sprite_packs.get(robot_sprite_pack) is None:
            raise Exception(
                f"Robot sprite pack '{robot_sprite_pack}' is undefined'")
        crate_sprite_pack = level_theme_data["sprite_packs"]["crate"]
        if sprite_packs.get(crate_sprite_pack) is None:
            raise Exception(
                f"Crate sprite pack '{crate_sprite_pack}' is undefined'")

        themes.append(LevelTheme(layers, background_generator, thumbnail_colors, robot_sprite_pack,
                                 crate_sprite_pack))

    return themes


def _extract_thumbnail_colors(data: Any) -> Dict[Tile, int]:
    thumbnail_colors: Dict[Tile, int] = {}

    for tile in list(Tile):
        thumbnail_colors[tile] = data[tile.tile_name]

    return thumbnail_colors
