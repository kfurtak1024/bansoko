import logging


def process_skin_packs(input_data, sprites):
    skin_packs = {}

    for skin_pack_name, skin_pack_data in input_data.items():
        # TODO: Under construction!
        skin_packs[skin_pack_name] = skin_pack_data
        logging.info("Skin pack '%s' added", skin_pack_name)

    logging.info("Total skin packs: %d", len(skin_packs))
    return skin_packs
