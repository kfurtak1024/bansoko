"""Module for processing sprite packs."""
import logging
from typing import Any, Dict

from resbuilder import ResourceError


def process_sprite_packs(input_data: Any, sprites: Dict[str, Any]) -> Dict[str, Any]:
    """Process sprite packs from input resource file.

    :param input_data: input data from JSON file (root -> sprite_packs)
    :param sprites: collection of all processed sprites that sprite pack can refer to
    :return: processed sprite packs (ready to be serialized to JSON)
    """
    sprite_packs = {}

    for sprite_pack_name, sprite_pack_data in input_data.items():
        verified_sprites = []
        for sprite_name in sprite_pack_data:
            if sprites.get(sprite_name) is None:
                raise ResourceError(
                    f"Sprite pack '{sprite_pack_name}' refers to unknown sprite '{sprite_name}'")
            verified_sprites.append(sprite_name)

        sprite_packs[sprite_pack_name] = verified_sprites
        logging.info("Sprite pack '%s' added", sprite_pack_name)

    logging.info("Total sprite packs: %d", len(sprite_packs))
    return sprite_packs
