import logging
import random
from typing import Dict, NamedTuple, Optional

from resbuilder.processors.tiles import TilePacker


class TilemapGenerator(NamedTuple):
    tiles_probs: Dict[int, int]

    def next_tile(self) -> Optional[int]:
        if not self.tiles_probs:
            return None
        return random.choices(list(self.tiles_probs.keys()), list(self.tiles_probs.values())).pop()


def process_tilemap_generators(input_data, tile_packer: TilePacker) -> Dict[str, TilemapGenerator]:
    generators: Dict[str, TilemapGenerator] = {}

    for generator_name, generator_data in input_data.items():
        tiles_probs = {}
        for tile_filename, tile_probability in generator_data.items():
            tile_id = tile_packer.pack_tile(tile_filename)
            tiles_probs[tile_id] = tile_probability

        generators[generator_name] = TilemapGenerator(tiles_probs)
        logging.info("Tilemap generator '%s' added", generator_name)

    logging.info("Total tilemap generators: %d", len(generators))

    return generators