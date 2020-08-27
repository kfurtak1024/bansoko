import logging


def process_backgrounds(input_data):
    backgrounds = {}
    for background_name, background_data in input_data.items():
        # TODO: Under construction!
        backgrounds[background_name] = background_data
        logging.info("Background '%s' added", background_name)

    logging.info("Total backgrounds: %d", len(backgrounds))
    return backgrounds
