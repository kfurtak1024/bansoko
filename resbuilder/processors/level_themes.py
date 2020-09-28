from typing import Dict, List, NamedTuple

from resbuilder.processors.tiles import Tile


class LevelTheme(NamedTuple):
    tiles_ids: List[Dict[Tile, int]]
    background_generator: str
    thumbnail_colors: Dict[Tile, int]
    robot_skin: str
    crate_skin: str

    @property
    def num_layers(self) -> int:
        return len(self.tiles_ids)

    def tile_id(self, layer: int, tile: Tile) -> int:
        return self.tiles_ids[layer].get(tile, self.tiles_ids[0][Tile.VOID])

    def thumbnail_color(self, tile: Tile) -> int:
        return self.thumbnail_colors[tile]


def generate_level_themes(data, tile_packer, skin_packs) -> List[LevelTheme]:
    # TODO: Refactor it
    themes: List[LevelTheme] = []

    main_layers: List[Dict[Tile, int]] = []

    for level_theme_data in data["themes"]:
        main_layers.append(tile_packer.pack_level_theme(level_theme_data["tiles"]["layers"][0]))

    for i, level_theme_data in enumerate(data["themes"]):
        layers = [main_layers[i]]
        for j in range(1, 3):
            layers.append(tile_packer.pack_level_theme(level_theme_data["tiles"]["layers"][j]))

        background_generator = level_theme_data["background_generator"]
        thumbnail_colors = _extract_thumbnail_colors(level_theme_data["thumbnail_colors"])
        robot_skin = level_theme_data["skins"]["robot"]
        if skin_packs.get(robot_skin) is None:
            raise Exception(
                f"Robot skin '{robot_skin}' is undefined'")
        crate_skin = level_theme_data["skins"]["crate"]
        if skin_packs.get(crate_skin) is None:
            raise Exception(
                f"Skin '{crate_skin}' is undefined'")

        themes.append(
            LevelTheme(layers, background_generator, thumbnail_colors, robot_skin, crate_skin))

    return themes


def _extract_thumbnail_colors(data) -> Dict[Tile, int]:
    thumbnail_colors: Dict[Tile, int] = {}

    for tile in list(Tile):
        thumbnail_colors[tile] = data[tile.tile_name]

    return thumbnail_colors
