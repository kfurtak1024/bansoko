"""Module exposing a Bundle, which is a repository of sprites, backgrounds and level templates."""
import json
from typing import NamedTuple, List, Dict, Optional, Tuple

from bansoko.game.level import LevelTemplate
from bansoko.graphics import Rect, Point
from bansoko.graphics.background import Background, BackgroundElement
from bansoko.graphics.sprite import Sprite, SkinPack


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
        return len(self.level_templates)

    @property
    def last_level(self) -> int:
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


def load_sprites(input_data) -> Tuple[Sprite, ...]:
    sprites = []
    for sprite_data in input_data:
        sprites.append(Sprite(
            sprite_data["image_bank"],
            Rect.from_list(sprite_data["rect_uv"]),
            sprite_data["multilayer"],
            sprite_data["directional"],
            sprite_data["num_frames"]))

    return tuple(sprites)


def load_skin_packs(input_data, sprites: Tuple[Sprite, ...]) -> Dict[str, SkinPack]:
    skin_packs = {}

    for (skin_pack_name, skin_sprites) in input_data.items():
        skin_packs[skin_pack_name] = SkinPack([sprites[sprite_id] for sprite_id in skin_sprites])

    return skin_packs


def load_backgrounds(input_data, sprites: Tuple[Sprite, ...]) -> Dict[str, Background]:
    # TODO: Under construction!
    backgrounds = {}

    for (background_name, background_item) in input_data.items():
        color = background_item["background_color"]
        elements: List[BackgroundElement] = []
        if background_item.get("background_elements") is not None:
            for element in background_item["background_elements"]:
                elements.append(BackgroundElement(sprites[element["sprite"]],
                                                  Point.from_list(element["position"])))
        backgrounds[background_name] = Background(tuple(elements), color)

    return backgrounds


def load_level_templates(input_data) -> Tuple[LevelTemplate, ...]:
    # TODO: Under construction!
    return tuple([LevelTemplate(level_num, level["level_theme"]) for level_num, level in enumerate(input_data)])
