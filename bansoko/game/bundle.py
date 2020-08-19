"""Module exposing a Bundle, which is a repository of sprites, backgrounds and level templates."""
import json
from typing import NamedTuple, List, Dict, Optional, Tuple

from bansoko.game.level import LevelTemplate
from bansoko.game.tiles import TileSet
from bansoko.graphics import Rect, Point
from bansoko.graphics.background import Background, BackgroundElement
from bansoko.graphics.sprite import Sprite


class Bundle(NamedTuple):
    """
    Bundle is a central repository of game resources (such as: sprites, backgrounds
    and level templates).
    """

    sprites: Tuple[Sprite, ...]
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

    def get_level_template(self, template_id: int) -> Optional[LevelTemplate]:
        """
        Return level template with given template id.

        Arguments:
            template_id - id of template to be retrieved

        Returns:
            - instance of LevelTemplate with given id *OR*
            - None if there is no such a template in the bundle
        """
        return self.level_templates[template_id] \
            if template_id < len(self.level_templates) else None


# TODO: This is the most messy part so far!


def load_bundle(metadata_filename: str) -> Bundle:
    with open(metadata_filename) as metadata_file:
        metadata = json.load(metadata_file)
        sprites = load_sprites(metadata["sprites"])
        backgrounds = load_backgrounds(metadata["backgrounds"], sprites)

        # TODO: Refactor it!!!
        level_themes = metadata["level_themes"]
        level_templates = load_level_templates(metadata["levels"], level_themes)

        return Bundle(sprites, backgrounds, level_templates)


def load_sprites(input_data) -> Tuple[Sprite, ...]:
    # TODO: Under construction!
    return tuple([Sprite(1, Rect.from_list(sprite["image_rect"])) for sprite in input_data])


def load_backgrounds(input_data, sprites: Tuple[Sprite, ...]) -> Dict[str, Background]:
    # TODO: Under construction!
    backgrounds = {}

    for (k, v) in input_data.items():
        color = v["background_color"]
        elements: List[BackgroundElement] = []
        if v.get("background_elements") is not None:
            for element in v["background_elements"]:
                elements.append(BackgroundElement(sprites[element["sprite"]],
                                                  Point.from_list(element["position"])))
        backgrounds[k] = Background(tuple(elements), color)

    return backgrounds


def load_level_templates(input_data, level_themes) -> Tuple[LevelTemplate, ...]:
    # TODO: Under construction!
    level_templates = []
    for level_num, level in enumerate(input_data):
        level_templates.append(
            LevelTemplate(level_num, TileSet(level_themes[level["level_theme"]]["tiles"])))

    return tuple(level_templates)