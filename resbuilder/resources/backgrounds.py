"""Module for processing backgrounds from resource input file."""
import logging
import random
from typing import Dict, Tuple, Generator, Any, List

import pyxel

from bansoko import TILEMAP_HEIGHT, TILEMAP_WIDTH, LEVEL_WIDTH, LEVEL_HEIGHT
from bansoko.graphics import Point
from resbuilder.resources.tilemap_generators import TilemapGenerator

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
    tilemap_rects = _tilemap_uvs()
    for i, (background_name, background_data) in enumerate(input_data.items()):
        background = {}

        background_color = background_data.get("background_color")
        if background_color:
            background["background_color"] = background_color

        background_tilemap_data = background_data.get("background_tilemap")
        if background_tilemap_data:
            background["background_tilemap"] = _process_tilemap(background_tilemap_data,
                                                                i, tilemap_rects,
                                                                tilemap_generators)

        if background_data.get("elements"):
            background["elements"] = _process_elements(background_data["elements"],
                                                       background_name, sprites)

        backgrounds[background_name] = background
        logging.info("Background '%s' added", background_name)

    logging.info("Total backgrounds: %d", len(backgrounds))
    return backgrounds


def _generate_tilemap(seed: int, offset: Point, tile_generator: TilemapGenerator) -> None:
    random.seed(seed)
    for y in range(LEVEL_HEIGHT):
        for x in range(LEVEL_WIDTH):
            tile = tile_generator.next_tile()
            if tile:
                pyxel.tilemap(BACKGROUND_TILEMAP_ID).set(offset.x + x, offset.y + y, tile)


def _process_tilemap(tilemap_data: Any, background_num: int,
                     tilemap_rects: Generator[Tuple[int, ...], None, None],
                     tilemap_generators: Dict[str, TilemapGenerator]) -> Dict[str, Any]:
    tilemap_uv = next(tilemap_rects)
    seed = tilemap_data.get("seed", background_num)
    generator_name = tilemap_data["generator"]
    _generate_tilemap(seed, Point(tilemap_uv[0], tilemap_uv[1]),
                      tilemap_generators[generator_name])

    return {
        "tilemap_id": BACKGROUND_TILEMAP_ID,
        "tilemap_uv": tilemap_uv
    }


def _process_elements(elements_data: Any, background_name: str, sprites: Dict[str, Any]) \
        -> List[Any]:
    elements = []
    for element in elements_data:
        sprite_name = element["sprite"]
        if sprites.get(sprite_name) is None:
            raise Exception(
                f"Background '{background_name}' refers to unknown sprite '{sprite_name}'")
        elements.append({"sprite": sprite_name, "position": element["position"]})

    return elements


# TODO: Should we promote it, so it can be used in other modules (like levels?)
def _tilemap_uvs() -> Generator[Tuple[int, ...], None, None]:
    tilemaps_horizontally = TILEMAP_WIDTH // LEVEL_WIDTH
    tilemaps_vertically = TILEMAP_HEIGHT // LEVEL_HEIGHT
    num_of_tilemaps = tilemaps_horizontally * tilemaps_vertically
    for i in range(num_of_tilemaps):
        yield i % tilemaps_horizontally * LEVEL_WIDTH, \
              i // tilemaps_horizontally * LEVEL_WIDTH, \
              LEVEL_WIDTH, LEVEL_HEIGHT
