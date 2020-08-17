from collections import namedtuple
from pathlib import Path

import pyxel


def process_sprites(base_dir: str, input_data):
    # TODO: What a mess!!
    sprites = []
    packer = SpriteSheetPacker(1, base_dir)

    for sprite_data in input_data:
        rect = packer.pack_sprite(sprite_data["image"],
                                  Rect(sprite_data["image_rect"][0], sprite_data["image_rect"][1],
                                       sprite_data["image_rect"][2], sprite_data["image_rect"][3]))
        sprites.append({
            "image_bank": 1,
            "image_rect": [rect.x, rect.y, rect.w, rect.h]
        })

    return sprites


Rect = namedtuple("Rect", ["x", "y", "w", "h"])


# TODO: Temporary implementation
class SpriteSheetPacker:
    def __init__(self, image_bank: int, base_dir: str):
        self.image_bank = image_bank
        self.base_dir = base_dir
        # TODO: Reimplement
        self.start_y = 0

    def pack_sprite(self, filename: str, src_rect: Rect) -> Rect:
        rect = Rect(0, self.start_y, src_rect.w, src_rect.h)
        pyxel.image(self.image_bank).load(rect.x, rect.y, Path(self.base_dir).joinpath(filename))

        self.start_y += src_rect.h

        return rect
