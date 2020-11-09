"""Module for processing backgrounds from resource input file."""
import logging
from typing import Dict, Any, List

from bansoko.graphics import Rect
from resbuilder import ResourceError
from resbuilder.resources.background_tilemaps import TilemapGenerator, WindowTileset
from resbuilder.resources.tiles import tilemap_rect_nth

BACKGROUND_TILEMAP_ID: int = 7


def process_backgrounds(input_data: Any, sprites: Dict[str, Any],
                        tilemap_generators: Dict[str, TilemapGenerator],
                        window_tilesets: Dict[str, WindowTileset]) -> Dict[str, Any]:
    """Process backgrounds from input resource file.

    :param input_data: input data from JSON file (root -> backgrounds)
    :param sprites: collection of all processed sprites that background can refer to
    :param tilemap_generators: collection of processed tilemap generators that background can use
    :param window_tilesets: collection of processed window tilesets that background can use
    :return: processed backgrounds (ready to be serialized to JSON)
    """
    backgrounds = {}
    tilemap_num = 0
    for background_name, background_data in input_data.items():
        background = {}

        background_color = background_data.get("background_color")
        if background_color:
            background["background_color"] = background_color

        background_tilemap_data = background_data.get("background_tilemap")
        if background_tilemap_data:
            generator_data = background_tilemap_data.get("tilemap_generator")
            if generator_data:
                _generate_tilemap(tilemap_num, generator_data, tilemap_generators)
            windows_data = background_tilemap_data.get("background_windows")
            if windows_data:
                _process_windows(tilemap_num, windows_data, window_tilesets)
            background["background_tilemap"] = {
                "tilemap_id": BACKGROUND_TILEMAP_ID,
                "tilemap_uv": tilemap_rect_nth(tilemap_num).as_list
            }
            tilemap_num += 1

        if background_data.get("elements"):
            background["elements"] = _process_elements(background_data["elements"],
                                                       background_name, sprites)

        backgrounds[background_name] = background
        logging.info("Background '%s' added", background_name)

    logging.info("Total backgrounds: %d", len(backgrounds))
    return backgrounds


def _generate_tilemap(tilemap_num: int, generator_data: Any,
                      tilemap_generators: Dict[str, TilemapGenerator]) -> None:
    tilemap_rect = tilemap_rect_nth(tilemap_num)
    seed = generator_data.get("seed", tilemap_num)
    generator = tilemap_generators[generator_data["generator_name"]]
    generator.generate_tilemap(BACKGROUND_TILEMAP_ID, tilemap_rect, seed)


def _process_windows(tilemap_num: int, window_tileset_data: Any,
                     window_tilesets: Dict[str, WindowTileset]) -> None:
    tilemap_rect = tilemap_rect_nth(tilemap_num)
    for window_data in window_tileset_data:
        window_tileset = window_tilesets[window_data["tileset_name"]]
        window_rect = Rect.from_list(window_data["rect"]).offset(tilemap_rect.position)
        window_tileset.draw_window(BACKGROUND_TILEMAP_ID, window_rect)


def _process_elements(elements_data: Any, background_name: str, sprites: Dict[str, Any]) \
        -> List[Any]:
    elements = []
    for element in elements_data:
        sprite_name = element["sprite"]
        if sprites.get(sprite_name) is None:
            raise ResourceError(
                f"Background '{background_name}' refers to unknown sprite '{sprite_name}'")
        elements.append({"sprite": sprite_name, "position": element["position"]})

    return elements
