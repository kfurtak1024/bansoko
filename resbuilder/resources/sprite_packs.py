import logging
from typing import Any, Dict


def process_sprite_packs(input_data: Any, sprites: Dict[str, Any]) -> Dict[str, Any]:
    sprite_packs = {}

    for sprite_pack_name, sprite_pack_data in input_data.items():
        # TODO: Under construction!
        sprite_packs[sprite_pack_name] = sprite_pack_data
        logging.info("Sprite pack '%s' added", sprite_pack_name)

    logging.info("Total sprite packs: %d", len(sprite_packs))
    return sprite_packs
