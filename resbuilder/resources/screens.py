"""Module for processing screens from resource input file."""
import logging
from typing import Dict, Any, List

from bansoko.graphics import Rect
from resbuilder import ResourceError
from resbuilder.resources.backgrounds import TilemapGenerator, NineSlicingFrame
from resbuilder.resources.tiles import tilemap_rect_nth

BACKGROUND_TILEMAP_ID: int = 7


def process_screens(input_data: Any, sprites: Dict[str, Any],
                    tilemap_generators: Dict[str, TilemapGenerator],
                    frame_tilesets: Dict[str, NineSlicingFrame]) -> Dict[str, Any]:
    """Process screens from input resource file.

    :param input_data: input data from JSON file (root -> screens)
    :param sprites: collection of all processed sprites that screen can refer to
    :param tilemap_generators: collection of processed tilemap generators that screen can use
    :param frame_tilesets: collection of processed frame tilesets that screen can use
    :return: processed screens (ready to be serialized to JSON)
    """
    screens = {}
    tilemap_num = 0
    for screen_name, screen_data in input_data.items():
        screen: Dict[str, Any] = {}

        background_data = screen_data.get("background")
        if background_data:
            screen_background: Dict[str, Any] = {}
            background_color = background_data.get("background_color")
            if background_color:
                screen_background["background_color"] = int(background_color, 16)

            generator_data = background_data.get("tilemap_generator")
            if generator_data:
                _generate_tilemap(tilemap_num, generator_data, tilemap_generators)

            frames_data = background_data.get("frames")
            if frames_data:
                _process_frames(tilemap_num, frames_data, frame_tilesets)

            if generator_data or frames_data:
                screen_background["background_tilemap"] = {
                    "tilemap_id": BACKGROUND_TILEMAP_ID,
                    "tilemap_uv": tilemap_rect_nth(tilemap_num).as_list
                }
                tilemap_num += 1

            if screen_background:
                screen["background"] = screen_background

        if screen_data.get("elements"):
            screen["elements"] = _process_elements(
                screen_data["elements"], screen_name, sprites)

        if screen_data.get("menu"):
            screen["menu"] = _process_menu(screen_data["menu"])

        screens[screen_name] = screen
        logging.info("Screen '%s' added", screen_name)

    logging.info("Total screens: %d", len(screens))
    return screens


def _generate_tilemap(tilemap_num: int, generator_data: Any,
                      tilemap_generators: Dict[str, TilemapGenerator]) -> None:
    tilemap_rect = tilemap_rect_nth(tilemap_num)
    seed = generator_data.get("seed", tilemap_num)
    generator = tilemap_generators[generator_data["generator_ref"]]
    generator.generate_tilemap(BACKGROUND_TILEMAP_ID, tilemap_rect, seed)


def _process_frames(tilemap_num: int, frame_tileset_data: Any,
                    frame_tilesets: Dict[str, NineSlicingFrame]) -> None:
    tilemap_rect = tilemap_rect_nth(tilemap_num)
    for frame_data in frame_tileset_data:
        frame_tileset = frame_tilesets[frame_data["tileset_ref"]]
        frame_rect = Rect.from_list(frame_data["rect"]).offset(tilemap_rect.position)
        frame_tileset.draw_frame(BACKGROUND_TILEMAP_ID, frame_rect)


def _process_elements(elements_data: Any, screen_name: str, sprites: Dict[str, Any]) -> List[Any]:
    elements = []
    for element_data in elements_data:
        element = {"position": element_data["position"]}
        if element_data.get("sprite_ref"):
            sprite_name = element_data["sprite_ref"]
            if sprites.get(sprite_name) is None:
                raise ResourceError(
                    f"Screen '{screen_name}' refers to unknown sprite '{sprite_name}'")
            element["sprite_ref"] = sprite_name
        elif element_data.get("text"):
            element["text"] = element_data["text"]
        elements.append(element)

    return elements


def _process_menu(screen_menu_data: Any) -> Dict[str, Any]:
    screen_menu = {}
    if screen_menu_data.get("position"):
        screen_menu["position"] = screen_menu_data["position"]
    if screen_menu_data.get("scrollbar_rect"):
        screen_menu["scrollbar_rect"] = screen_menu_data["scrollbar_rect"]
    return screen_menu
