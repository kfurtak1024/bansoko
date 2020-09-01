"""Module exposing a Bundle, which is a repository of sprites, backgrounds and level templates."""
import json
from typing import NamedTuple, Dict, Optional, Tuple

from bansoko.game.level import LevelTemplate
from bansoko.graphics import Rect, Point
from bansoko.graphics.background import Background, BackgroundElement
from bansoko.graphics.sprite import Sprite, SkinPack


# TODO: Consider renaming "bundle" (maybe game_pack?)


class Bundle(NamedTuple):
    """
    Bundle is a central repository of game resources (such as: sprites, backgrounds
    and level templates).
    """

    sprites: Tuple[Sprite, ...]
    skin_packs: Dict[str, SkinPack]
    backgrounds: Dict[str, Background]
    level_templates: Tuple[LevelTemplate, ...]

    def get_sprite(self, sprite_id: int) -> Optional[Sprite]:
        """
        Return sprite with given sprite id.

        Arguments:
            sprite_id - id of sprite to be retrieved

        Returns:
            - instance of Sprite with given id *OR*
            - None if there is no such a sprite in the bundle
        """
        return self.sprites[sprite_id] if sprite_id < len(self.sprites) else None

    def get_skin_pack(self, skin_pack_name: str) -> SkinPack:
        """
        Return skin pack with given skin pack name.

        Arguments:
            skin_pack_name - name of skin pack to be retrieved

        Returns:
            - instance of SkinPack with given name
        """
        return self.skin_packs[skin_pack_name]

    def get_background(self, background_name: str) -> Optional[Background]:
        """
        Return background with given background name.

        Arguments:
            background_name - name of background to be retrieved

        Returns:
            - instance of Background with given name *OR*
            - None if there is no such a background in the bundle
        """
        return self.backgrounds.get(background_name, None)

    def get_level_template(self, template_id: int) -> LevelTemplate:
        """
        Return level template with given template id.

        Arguments:
            template_id - id of template to be retrieved

        Returns:
            - instance of LevelTemplate with given id
        """
        return self.level_templates[template_id]

    @property
    def num_levels(self) -> int:
        """
        Return total number of levels in bundle.

        Returns:
            - total number of levels bundle contains
        """
        return len(self.level_templates)

    @property
    def last_level(self) -> int:
        """
        Return index of the last level in bundle.

        Returns:
            - index of the last level bundle contains
        """
        return self.num_levels - 1


# TODO: This is the most messy part so far!


def load_bundle(metadata_filename: str) -> Bundle:
    with open(metadata_filename) as metadata_file:
        metadata = json.load(metadata_file)
        sprites = load_sprites(metadata["sprites"])
        skin_packs = load_skin_packs(metadata["skin_packs"], sprites)
        backgrounds = load_backgrounds(metadata["backgrounds"], sprites)
        level_templates = load_level_templates(metadata["levels"])
        return Bundle(sprites, skin_packs, backgrounds, level_templates)


def load_sprites(json_data) -> Tuple[Sprite, ...]:
    return tuple([__sprite_from_json(data) for data in json_data])


def __sprite_from_json(sprite_json) -> Sprite:
    return Sprite(
        sprite_json["image_bank"],
        Rect.from_list(sprite_json["uv_rect"]),
        sprite_json["multilayer"],
        sprite_json["directional"],
        sprite_json["num_frames"])


def load_skin_packs(json_data, sprites: Tuple[Sprite, ...]) -> Dict[str, SkinPack]:
    return {name: __skin_pack_from_json(data, sprites) for (name, data) in json_data.items()}


def __skin_pack_from_json(skin_pack_json, sprites: Tuple[Sprite, ...]) -> SkinPack:
    return SkinPack([sprites[sprite_id] for sprite_id in skin_pack_json])


def load_backgrounds(json_data, sprites: Tuple[Sprite, ...]) -> Dict[str, Background]:
    return {name: __background_from_json(data, sprites) for (name, data) in json_data.items()}


def __background_from_json(json_data, sprites: Tuple[Sprite, ...]) -> Background:
    color = json_data["color"]
    if json_data.get("elements") is None:
        return Background(tuple(), color)

    return Background(tuple([__background_element_from_json(data, sprites) for data in json_data["elements"]]), color)


def __background_element_from_json(json_data, sprites: Tuple[Sprite, ...]) -> BackgroundElement:
    return BackgroundElement(sprites[json_data["sprite"]], Point.from_list(json_data["position"]))


def load_level_templates(json_data) -> Tuple[LevelTemplate, ...]:
    return tuple([__level_template_from_json(level, level_num) for level_num, level in enumerate(json_data)])


def __level_template_from_json(json_data, level_num: int) -> LevelTemplate:
    return LevelTemplate(level_num, json_data["theme"])
