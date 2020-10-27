"""Module for processing backgrounds from resource input file."""
import logging
from typing import Dict, Any, List

from resbuilder import ResourceError
from resbuilder.resources.tilemap_generators import TilemapGenerator
from resbuilder.resources.tiles import tilemap_rect_nth

BACKGROUND_TILEMAP_ID: int = 7


def process_backgrounds(input_data: Any, sprites: Dict[str, Any],
                        tilemap_generators: Dict[str, TilemapGenerator]) -> Dict[str, Any]:
    """Process backgrounds from input resource file.

    :param input_data: input data from JSON file (root -> backgrounds)
    :param sprites: collection of all processed sprites that background can refer to
    :param tilemap_generators: collection of processed tilemap generators that background can use
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
            seed = background_tilemap_data.get("seed", tilemap_num)
            generator_name = background_tilemap_data["generator"]
            generator = tilemap_generators[generator_name]
            background["background_tilemap"] = _generate_tilemap(tilemap_num, generator, seed)
            tilemap_num += 1

        if background_data.get("elements"):
            background["elements"] = _process_elements(background_data["elements"],
                                                       background_name, sprites)

        backgrounds[background_name] = background
        logging.info("Background '%s' added", background_name)

    logging.info("Total backgrounds: %d", len(backgrounds))
    return backgrounds


def _generate_tilemap(tilemap_num: int, tilemap_generator: TilemapGenerator,
                      seed: int) -> Dict[str, Any]:
    tilemap_rect = tilemap_rect_nth(tilemap_num)
    tilemap_generator.generate_tilemap(BACKGROUND_TILEMAP_ID, tilemap_rect, seed)
    return {
        "tilemap_id": BACKGROUND_TILEMAP_ID,
        "tilemap_uv": tilemap_rect.as_list
    }


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
