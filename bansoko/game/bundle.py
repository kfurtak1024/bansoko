import json
from typing import NamedTuple, List, Dict

from game.level import LevelTemplate
from game.tiles import TileSet
from graphics import Rect, Point
from graphics.background import Background, BackgroundElement
from graphics.sprite import Sprite

# TODO: This is the most messy part so far!


class Bundle(NamedTuple):
    sprites: List[Sprite]
    backgrounds: Dict[str, Background]
    level_templates: List[LevelTemplate]

    def get_sprite(self, sprite: int) -> Sprite:
        return self.sprites[sprite] if sprite < len(self.sprites) else None

    def get_background(self, name: str) -> Background:
        return self.backgrounds.get(name, None)

    def get_level_template(self, template: int) -> LevelTemplate:
        return self.level_templates[template] if template < len(self.level_templates) else None


def load_bundle(metadata_file: str) -> Bundle:
    with open(metadata_file) as metadata_file:
        metadata = json.load(metadata_file)
        sprites = _load_sprites(metadata["sprites"])
        backgrounds = _load_backgrounds(metadata["backgrounds"], sprites)

        # TODO: Refactor it!!!
        level_themes = metadata["level_themes"]
        level_templates = _load_level_templates(metadata["levels"], level_themes)

        return Bundle(sprites, backgrounds, level_templates)


def _load_sprites(input_data) -> List[Sprite]:
    # TODO: Under construction!
    sprites: List[Sprite] = []
    for sprite_data in input_data:
        sprites.append(Sprite(1, Rect(sprite_data["image_rect"][0], sprite_data["image_rect"][1],
                                      sprite_data["image_rect"][2], sprite_data["image_rect"][3])))

    return sprites


def _load_backgrounds(input_data, sprites: List[Sprite]) -> Dict[str, Background]:
    # TODO: Under construction!
    backgrounds = {}

    for (k, v) in input_data.items():
        background_color = v["background_color"]
        background_elements: List[BackgroundElement] = []
        if v.get("background_elements") is not None:
            for element in v["background_elements"]:
                background_elements.append(BackgroundElement(sprites[element["sprite"]],
                                                             Point(element["position"][0],
                                                                   element["position"][1])))
        backgrounds[k] = Background(background_elements, background_color)

    return backgrounds


def _load_level_templates(input_data, level_themes) -> List[LevelTemplate]:
    # TODO: Under construction!
    level_templates = []
    for level_num, level in enumerate(input_data):
        level_templates.append(
            LevelTemplate(level_num, TileSet(level_themes[level["level_theme"]]["tiles"])))

    return level_templates
