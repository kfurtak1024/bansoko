"""Module for processing screens from resource input file."""
import logging
from typing import Dict, Any, List

from bansoko.graphics import Rect
from resbuilder import ResourceError
from resbuilder.resources.background_tilemaps import TilemapGenerator, WindowTileset
from resbuilder.resources.tiles import tilemap_rect_nth

BACKGROUND_TILEMAP_ID: int = 7


def process_screens(input_data: Any, sprites: Dict[str, Any],
                    tilemap_generators: Dict[str, TilemapGenerator],
                    window_tilesets: Dict[str, WindowTileset]) -> Dict[str, Any]:
    """Process screens from input resource file.

    :param input_data: input data from JSON file (root -> screens)
    :param sprites: collection of all processed sprites that screen can refer to
    :param tilemap_generators: collection of processed tilemap generators that screen can use
    :param window_tilesets: collection of processed window tilesets that screen can use
    :return: processed screens (ready to be serialized to JSON)
    """
    screens = {}
    tilemap_num = 0
    for screen_name, screen_data in input_data.items():
        screen: Dict[str, Any] = {}

        background_color = screen_data.get("background_color")
        if background_color:
            screen["background_color"] = int(background_color, 16)

        background_tilemap_data = screen_data.get("background_tilemap")
        if background_tilemap_data:
            generator_data = background_tilemap_data.get("tilemap_generator")
            if generator_data:
                _generate_tilemap(tilemap_num, generator_data, tilemap_generators)
            windows_data = background_tilemap_data.get("background_windows")
            if windows_data:
                _process_windows(tilemap_num, windows_data, window_tilesets)
            screen["background_tilemap"] = {
                "tilemap_id": BACKGROUND_TILEMAP_ID,
                "tilemap_uv": tilemap_rect_nth(tilemap_num).as_list
            }
            tilemap_num += 1

        if screen_data.get("screen_elements"):
            screen["screen_elements"] = _process_elements(
                screen_data["screen_elements"], screen_name, sprites)

        if screen_data.get("screen_menu"):
            screen_menu = {}
            screen_menu_data = screen_data["screen_menu"]
            if screen_menu_data.get("position"):
                screen_menu["position"] = screen_menu_data["position"]
            if screen_menu_data.get("scrollbar_rect"):
                screen_menu["scrollbar_rect"] = screen_menu_data["scrollbar_rect"]
            screen["screen_menu"] = screen_menu

        screens[screen_name] = screen
        logging.info("Screen '%s' added", screen_name)

    logging.info("Total screens: %d", len(screens))
    return screens


def _generate_tilemap(tilemap_num: int, generator_data: Any,
                      tilemap_generators: Dict[str, TilemapGenerator]) -> None:
    tilemap_rect = tilemap_rect_nth(tilemap_num)
    seed = generator_data.get("seed", tilemap_num)
    generator = tilemap_generators[generator_data["generator_name"]]
    generator.generate_tilemap(BACKGROUND_TILEMAP_ID, tilemap_rect, seed)


def _process_windows(tilemap_num: int, window_tileset_data: Any,
                     window_tilesets: Dict[str, WindowTileset]) -> None:
    tilemap_rect = tilemap_rect_nth(tilemap_num)
    for window_data in window_tileset_data:
        window_tileset = window_tilesets[window_data["tileset_name"]]
        window_rect = Rect.from_list(window_data["rect"]).offset(tilemap_rect.position)
        window_tileset.draw_window(BACKGROUND_TILEMAP_ID, window_rect)


def _process_elements(elements_data: Any, screen_name: str, sprites: Dict[str, Any]) -> List[Any]:
    elements = []
    for element_data in elements_data:
        element = {"position": element_data["position"]}
        if element_data.get("sprite"):
            sprite_name = element_data["sprite"]
            if sprites.get(sprite_name) is None:
                raise ResourceError(
                    f"Screen '{screen_name}' refers to unknown sprite '{sprite_name}'")
            element["sprite"] = sprite_name
        elif element_data.get("text"):
            element["text"] = element_data["text"]
        elements.append(element)

    return elements
