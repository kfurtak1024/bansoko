"""Module exposing a Bundle, which is a repository of sprites, screens and level templates."""
from dataclasses import dataclass
from json import JSONDecodeError, load
from typing import Dict, Tuple, Any

from jsonschema import validate, ValidationError

from bansoko.game import GameError
from bansoko.game.level_template import LevelTemplate, LevelSpritePacks
from bansoko.game.metadata_schema import METADATA_JSON_SCHEMA
from bansoko.game.screens.gui_consts import GuiConsts, GuiPosition, GuiColor, GuiSprite
from bansoko.graphics import Rect, Point
from bansoko.graphics.sprite import Sprite, SpritePack
from bansoko.graphics.tilemap import Tilemap
from bansoko.gui.screen import Screen, ScreenElement

SHA1_SIZE_IN_BYTES = 40


@dataclass(frozen=True)
class Bundle:
    """Bundle is a central repository of game resources (such as: sprites, screens
    and level templates)."""

    sha1: bytearray
    sprites: Dict[str, Sprite]
    sprite_packs: Dict[str, SpritePack]
    screens: Dict[str, Screen]
    gui_consts: GuiConsts
    level_templates: Tuple[LevelTemplate, ...]

    def get_sprite(self, sprite_name: str) -> Sprite:
        """ Return sprite with given sprite name.

        :param sprite_name: name of sprite to be retrieved
        :return: instance of Sprite with given name
        """
        return self.sprites[sprite_name]

    def get_sprite_pack(self, sprite_pack_name: str) -> SpritePack:
        """Return sprite pack with given name.

        :param sprite_pack_name: name of sprite pack to be retrieved
        :return: instance of SpritePack with given name
        """
        return self.sprite_packs[sprite_pack_name]

    def get_gui_consts(self) -> GuiConsts:
        """Return Gui constants."""
        return self.gui_consts

    def get_screen(self, screen_name: str) -> Screen:
        """Return screen with given screen name.

        :param screen_name: name of screen to be retrieved
        :return: instance of Screen with given name
        """
        return self.screens[screen_name]

    def get_level_template(self, template_id: int) -> LevelTemplate:
        """Return level template with given template id.

        :param template_id: id of template to be retrieved
        :return: instance of LevelTemplate with given id
        """
        return self.level_templates[template_id]

    @property
    def num_levels(self) -> int:
        """Total number of levels in bundle.

        :return: total number of levels bundle contains
        """
        return len(self.level_templates)

    @property
    def last_level(self) -> int:
        """Index of the last level in bundle.

        :return: index of the last level bundle contains
        """
        return self.num_levels - 1


def load_bundle(metadata_filename: str) -> Bundle:
    """Load game resources into bundle using metadata file.

    :param metadata_filename: name of the metadata file
    :return: bundle with game resources
    """
    try:
        with open(metadata_filename) as metadata_file:
            metadata = load(metadata_file)
            validate(metadata, METADATA_JSON_SCHEMA)
            sprites = create_sprites(metadata["sprites"])
            sprite_packs = create_sprite_packs(metadata["sprite_packs"], sprites)
            screens = create_screens(metadata["screens"], sprites)
            gui_consts = create_gui_consts(metadata["gui_consts"], sprites)
            sha1 = bytearray(metadata["levels"]["sha1"], "utf-8").zfill(
                SHA1_SIZE_IN_BYTES)[-SHA1_SIZE_IN_BYTES:]
            level_templates = create_level_templates(
                metadata["levels"]["level_templates"], sprite_packs)
            return Bundle(sha1, sprites, sprite_packs, screens, gui_consts, level_templates)
    except JSONDecodeError as decode_error:
        raise GameError("Incorrect format of resource metadata file") from decode_error
    except ValidationError as validation_error:
        raise GameError("Incorrect format of resource metadata file") from validation_error


def create_sprites(json_data: Any) -> Dict[str, Sprite]:
    """Create sprites from metadata.

    :param json_data: input JSON containing sprites metadata
    :return: collection of sprites
    """
    return {
        name: Sprite(
            image_bank=data["image_bank"],
            uv_rect=Rect.from_list(data["uv_rect"]),
            directional=data["directional"],
            transparency_color=data["transparency_color"],
            num_layers=data["num_layers"],
            num_frames=data["num_frames"])
        for name, data in json_data.items()
    }


def create_sprite_packs(json_data: Any, sprites: Dict[str, Sprite]) -> Dict[str, SpritePack]:
    """Create sprite packs from metadata.

    :param json_data: input JSON containing sprite packs metadata
    :param sprites: collection of available sprites
    :return: collection of sprite packs
    """
    return {
        name: SpritePack(
            sprites=tuple([sprites[sprite_name] for sprite_name in data]))
        for (name, data) in json_data.items()
    }


def create_gui_consts(json_data: Any, sprites: Dict[str, Sprite]) -> GuiConsts:
    """Create Gui constants from metadata.

    :param json_data: input JSON containing Gui constants
    :param sprites: collection of available sprites
    :return: Gui constants
    """
    return GuiConsts(
        gui_positions=tuple([
            Point.from_list(json_data["positions"][pos.resource_name]) for pos in list(GuiPosition)
        ]),
        gui_colors=tuple([
            int(json_data["colors"][color.resource_name]) for color in list(GuiColor)
        ]),
        gui_sprites=tuple([
            sprites[json_data["sprites"][sprite.resource_name]] for sprite in list(GuiSprite)
        ]))


def create_screens(json_data: Any, sprites: Dict[str, Sprite]) -> Dict[str, Screen]:
    """Create screens from metadata.

    :param json_data: input JSON containing screens metadata
    :param sprites: collection of available sprites
    :return: collection of screens
    """
    return {
        name: _screen_from_json(data, sprites)
        for (name, data) in json_data.items()
    }


def _screen_from_json(json_data: Any, sprites: Dict[str, Sprite]) -> Screen:
    background_data = json_data.get("background")
    background_color = None
    background_tilemap = None
    if background_data:
        background_color = background_data.get("background_color")
        tilemap_data = background_data.get("background_tilemap")
        if tilemap_data:
            background_tilemap = Tilemap(
                tilemap_id=tilemap_data["tilemap_id"],
                rect_uv=Rect.from_list(tilemap_data["tilemap_uv"])
            )

    screen_elements = []
    if json_data.get("elements"):
        screen_elements = [
            ScreenElement(
                position=Point.from_list(data["position"]),
                sprite=sprites.get(data.get("sprite_ref")),
                text=data.get("text"))
            for data in json_data["elements"]
        ]
    menu_position = None
    menu_scrollbar_rect = None
    if json_data.get("menu"):
        menu_data = json_data["menu"]
        menu_position = \
            Point.from_list(menu_data["position"]) if menu_data.get("position") else None
        menu_scrollbar_rect = \
            Rect.from_list(menu_data["scrollbar_rect"]) if menu_data.get("scrollbar_rect") else None

    return Screen(
        background_color=background_color, background_tilemap=background_tilemap,
        elements=tuple(screen_elements), menu_position=menu_position,
        menu_scrollbar_rect=menu_scrollbar_rect)


def create_level_templates(json_data: Any, sprite_packs: Dict[str, SpritePack]) \
        -> Tuple[LevelTemplate, ...]:
    """Create level templates from metadata.

    :param json_data: input JSON containing level template metadata
    :param sprite_packs: collection of available sprite packs
    :return: collection of level templates
    """
    return tuple([
        LevelTemplate.from_level_num(
            level_num=level_num,
            tileset_index=data["tileset"],
            draw_offset=Point.from_list(data["draw_offset"]),
            sprite_packs=LevelSpritePacks(
                robot_sprite_pack=sprite_packs[data["robot_sprite_pack_ref"]],
                crate_sprite_pack=sprite_packs[data["crate_sprite_pack_ref"]]))
        for level_num, data in enumerate(json_data)])
