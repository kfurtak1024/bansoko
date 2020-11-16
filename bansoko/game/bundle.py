"""Module exposing a Bundle, which is a repository of sprites, screens and level templates."""
import json
from dataclasses import dataclass
from typing import Dict, Tuple, Any

from bansoko.game.level_template import LevelTemplate, LevelSpritePacks
from bansoko.graphics import Rect, Point
from bansoko.graphics.sprite import Sprite, SpritePack
from bansoko.graphics.tilemap import Tilemap
from bansoko.gui.screen import Screen, ScreenElement


@dataclass(frozen=True)
class Bundle:
    """Bundle is a central repository of game resources (such as: sprites, screens
    and level templates)."""

    sprites: Dict[str, Sprite]
    sprite_packs: Dict[str, SpritePack]
    screens: Dict[str, Screen]
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
    with open(metadata_filename) as metadata_file:
        metadata = json.load(metadata_file)
        sprites = create_sprites(metadata["sprites"])
        sprite_packs = create_sprite_packs(metadata["sprite_packs"], sprites)
        screens = create_screens(metadata["screens"], sprites)
        level_templates = create_level_templates(metadata["levels"], sprite_packs)
        return Bundle(sprites, sprite_packs, screens, level_templates)


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
            transparent=data["transparent"],
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
    background_color = json_data.get("background_color")
    tilemap_data = json_data.get("background_tilemap")
    tilemap = None
    if tilemap_data:
        tilemap = Tilemap(
            tilemap_id=tilemap_data["tilemap_id"],
            rect_uv=Rect.from_list(tilemap_data["tilemap_uv"])
        )
    screen_elements = []
    if json_data.get("screen_elements") is not None:
        screen_elements = [
            ScreenElement(
                position=Point.from_list(data["position"]),
                sprite=sprites.get(data.get("sprite")),
                text=data.get("text"))
            for data in json_data["screen_elements"]
        ]

    return Screen(tuple(screen_elements), background_color, tilemap)


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
                robot_sprite_pack=sprite_packs[data["robot_sprite_pack"]],
                crate_sprite_pack=sprite_packs[data["crate_sprite_pack"]]))
        for level_num, data in enumerate(json_data)])
