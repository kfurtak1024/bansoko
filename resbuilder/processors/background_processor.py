import logging


def process_backgrounds(input_data, sprites):
    # TODO: Under construction!
    backgrounds = {}
    for background_name, background_data in input_data.items():
        background = {}
        color = background_data.get("color")
        if color:
            background["color"] = color
        # TODO: Validate color

        if background_data.get("elements") is not None:
            elements = []
            for element in background_data["elements"]:
                sprite_name = element["sprite"]
                if sprites.get(sprite_name) is None:
                    raise Exception(
                        f"Background '{background_name}' refers to unknown sprite '{sprite_name}'")
                position = element["position"]
                elements.append({"sprite": sprite_name, "position": position})

            if elements:
                background["elements"] = elements

        backgrounds[background_name] = background
        logging.info("Background '%s' added", background_name)

    logging.info("Total backgrounds: %d", len(backgrounds))
    return backgrounds
