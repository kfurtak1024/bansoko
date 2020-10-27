"""Module exposing level theme generator."""
from dataclasses import dataclass
from typing import Dict, List, Any

from bansoko import LEVEL_NUM_LAYERS
from resbuilder import ResourceError
from resbuilder.resources.tiles import Tile, TilePacker


@dataclass(frozen=True)
class LevelTheme:
    """Level theme defines the look&feel of the level.

    Multiple levels can share the same level theme.

    Attributes:
        tiles_ids - collection of tilesets ordered by layer
        background_generator - generator used for generating level background
        thumbnail_colors - thumbnail colors for all types of tiles
        robot_sprite_pack - sprite pack containing all robot related sprites
        crate_sprite_pack - sprite pack containing all crate related sprites
    """
    tiles_ids: List[Dict[Tile, int]]
    background_generator: str
    thumbnail_colors: Dict[Tile, int]
    robot_sprite_pack: str
    crate_sprite_pack: str

    @property
    def num_layers(self) -> int:
        """Number of layers this level theme contains."""
        return len(self.tiles_ids)

    def tile_id(self, layer: int, tile: Tile) -> int:
        """Pyxel's mega-tilemap id for given tile type.

        :param layer: layer to determine tileset to get tile id from
        :param tile: tile to get Pyxel's mega-tilemap id for
        :return: tile id
        """
        return self.tiles_ids[layer].get(tile, self.tiles_ids[0][Tile.VOID])

    def thumbnail_color(self, tile: Tile) -> int:
        """Thumbnail color for given tile.

        :param tile: tile to get thumbnail color for
        :return: thumbnail color for given tile
        """
        return self.thumbnail_colors[tile]


def generate_level_themes(input_data: Any, tile_packer: TilePacker,
                          sprite_packs: Dict[str, Any]) -> List[LevelTheme]:
    """Generate level themes from input resource file.

    :param input_data: input data from JSON file (root -> level_themes)
    :param tile_packer: tile packer used to pack tiles generated for level themes
    :param sprite_packs: collection of available sprite packs
    :return: collection of generated level themes
    """
    themes: List[LevelTheme] = []
    main_layers: List[Dict[Tile, int]] = []

    for level_theme_data in input_data:
        main_layers.append(tile_packer.pack_tileset(level_theme_data["tiles"]["layers"][0]))

    for i, level_theme_data in enumerate(input_data):
        layers = [main_layers[i]]
        for j in range(1, LEVEL_NUM_LAYERS):
            layers.append(tile_packer.pack_tileset(level_theme_data["tiles"]["layers"][j]))

        background_generator = level_theme_data["background_generator"]
        # TODO: Check if background_generator exists
        thumbnail_colors = _extract_thumbnail_colors(level_theme_data["thumbnail_colors"])
        robot_sprite_pack = level_theme_data["sprite_packs"]["robot"]
        if sprite_packs.get(robot_sprite_pack) is None:
            raise ResourceError(
                f"Robot sprite pack '{robot_sprite_pack}' is undefined'")
        crate_sprite_pack = level_theme_data["sprite_packs"]["crate"]
        if sprite_packs.get(crate_sprite_pack) is None:
            raise ResourceError(
                f"Crate sprite pack '{crate_sprite_pack}' is undefined'")

        themes.append(LevelTheme(layers, background_generator, thumbnail_colors, robot_sprite_pack,
                                 crate_sprite_pack))

    return themes


def _extract_thumbnail_colors(data: Any) -> Dict[Tile, int]:
    thumbnail_colors: Dict[Tile, int] = {}

    for tile in list(Tile):
        thumbnail_colors[tile] = data[tile.tile_name]

    return thumbnail_colors
