"""Module for processing GUI constants."""
import logging
from typing import Any, Dict

from bansoko.game.screens.gui_consts import GuiPosition, GuiSprite, GuiColor
from resbuilder import ResourceError


def process_gui_consts(input_data: Any, sprites: Dict[str, Any]) -> Dict[str, Any]:
    """Process Gui constants from input resource file.

    :param input_data: input data from JSON file (root -> gui_consts)
    :param sprites: collection of all processed sprites that Gui constants can refer to
    :return: processed Gui constants (ready to be serialized to JSON)
    """
    gui_positions = {}
    positions_data = input_data["positions"]
    for gui_position in list(GuiPosition):
        gui_positions[gui_position.resource_name] = positions_data[gui_position.resource_name]

    gui_colors = {}
    colors_data = input_data["colors"]
    for gui_color in list(GuiColor):
        gui_colors[gui_color.resource_name] = int(colors_data[gui_color.resource_name], 16)

    gui_sprites = {}
    sprites_data = input_data["sprites"]
    for gui_sprite in list(GuiSprite):
        sprite_name = sprites_data[gui_sprite.resource_name]
        if sprites.get(sprite_name) is None:
            raise ResourceError(
                f"GUI constants refer to unknown sprite '{sprite_name}'")
        gui_sprites[gui_sprite.resource_name] = sprite_name

    logging.info("GUI constants processed")
    return {
        "positions": gui_positions,
        "colors": gui_colors,
        "sprites": gui_sprites
    }
