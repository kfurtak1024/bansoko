import logging
import random
from typing import Dict, Tuple, Generator

import pyxel

from resbuilder.processors.levels import Position
from resbuilder.processors.tilemap_generators import TilemapGenerator
from resbuilder.processors.tiles import IMAGE_BANK_SIZE

BACKGROUND_TILEMAP_ID: int = 7
BACKGROUND_WIDTH_IN_TILES: int = 32
BACKGROUND_HEIGHT_IN_TILES: int = 32


def process_backgrounds(input_data, sprites, tilemap_generators: Dict[str, TilemapGenerator]):
    # TODO: What a mess! Under construction!
    backgrounds = {}
    tilemap_rects = tilemap_uvs()
    for i, (background_name, background_data) in enumerate(input_data.items()):
        background = {}

        background_color = background_data.get("background_color")
        if background_color:
            background["background_color"] = background_color

        background_tilemap_data = background_data.get("background_tilemap")
        if background_tilemap_data:
            tilemap_uv = next(tilemap_rects)
            seed = background_tilemap_data.get("seed", i)
            generator_name = background_tilemap_data["generator"]
            _generate_background(seed, Position(tilemap_uv[0], tilemap_uv[1]), tilemap_generators[generator_name])
            background["background_tilemap"] = {
                "tilemap_id": BACKGROUND_TILEMAP_ID,
                "tilemap_uv": tilemap_uv
            }

        if background_data.get("elements") is not None:
            elements = []
            for element in background_data["elements"]:
                sprite_name = element["sprite"]
                if sprites.get(sprite_name) is None:
                    raise Exception(
                        f"Background '{background_name}' refers to unknown sprite '{sprite_name}'")
                elements.append({"sprite": sprite_name, "position": element["position"]})

            if elements:
                background["elements"] = elements

        backgrounds[background_name] = background
        logging.info("Background '%s' added", background_name)

    logging.info("Total backgrounds: %d", len(backgrounds))
    return backgrounds


def _generate_background(seed: int, offset: Position, tile_generator: TilemapGenerator) -> None:
    # TODO: Remove hard-codes!!
    random.seed(seed)
    for y in range(BACKGROUND_HEIGHT_IN_TILES):
        for x in range(BACKGROUND_WIDTH_IN_TILES):
            tile = tile_generator.next_tile()
            if tile:
                pyxel.tilemap(BACKGROUND_TILEMAP_ID).set(offset.x + x, offset.y + y, tile)


def tilemap_uvs() -> Generator[Tuple[int, ...], None, None]:
    tilemaps_horizontally = IMAGE_BANK_SIZE // BACKGROUND_WIDTH_IN_TILES
    tilemaps_vertically = IMAGE_BANK_SIZE // BACKGROUND_HEIGHT_IN_TILES
    num_of_tilemaps = tilemaps_horizontally * tilemaps_vertically
    for i in range(num_of_tilemaps):
        yield i % tilemaps_horizontally * 32, i // tilemaps_horizontally * 32, BACKGROUND_WIDTH_IN_TILES, BACKGROUND_HEIGHT_IN_TILES
