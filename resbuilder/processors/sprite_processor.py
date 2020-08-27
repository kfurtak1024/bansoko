import logging
from pathlib import Path
from typing import NamedTuple

import pyxel

from bansoko.graphics import Rect, Size
from graphics.sprite import Sprite


class SpriteMetadata(NamedTuple):
    image_bank: int
    rect_uv: Rect


# TODO: Temporary implementation
class SpriteSheetPacker:
    def __init__(self, image_bank: int, base_dir: str) -> None:
        # TODO: SpriteSheetPacker should decide which image_bank should be used
        self.image_bank = image_bank
        self.base_dir = base_dir
        # TODO: Reimplement!
        self.start_y = 0

    def pack_sprite(self, filename: str) -> SpriteMetadata:
        file_path = Path(self.base_dir).joinpath(filename)
        size = self.read_png_image_size(file_path)
        rect_uv = Rect.from_coords(0, self.start_y, size.width, size.height)
        pyxel.image(self.image_bank).load(rect_uv.x, rect_uv.y, file_path)

        self.start_y += size.height

        return SpriteMetadata(self.image_bank, rect_uv)

    @staticmethod
    def read_png_image_size(file_path: Path) -> Size:
        with open(file_path, "rb") as file:
            header = file.read(8)
            if header != bytes.fromhex("89 50 4E 47 0D 0A 1A 0A"):
                raise Exception(f"File '{file_path}' is not a valid PNG file")
            file.read(4)
            chunk_type = file.read(4)
            if chunk_type != b"IHDR":
                raise Exception(f"File '{file_path}' is not a valid PNG file")

            width = int.from_bytes(file.read(4), byteorder='big')
            height = int.from_bytes(file.read(4), byteorder='big')
            return Size(width, height)


def process_sprites(base_dir: str, sprite_list_data):
    packer = SpriteSheetPacker(1, base_dir)
    sprites = []

    for sprite_data in sprite_list_data:
        sprite_metadata = packer.pack_sprite(sprite_data["image"])

        sprite = Sprite(
            sprite_metadata.image_bank,
            sprite_metadata.rect_uv,
            sprite_data.get("multilayer", False),
            sprite_data.get("directional", False),
            sprite_data.get("num_frames", 1)
        )

        sprites.append({
            "image_bank": sprite.image_bank,
            "rect_uv": sprite.rect_uv.as_list,
            "multilayer": sprite.multilayer,
            "directional": sprite.directional,
            "num_frames": sprite.num_frames
        })
        logging.info("Sprite '%s' (%dx%d) added to image bank %d", sprite_data["image"],
                     sprite.width, sprite.height, sprite.image_bank)

    logging.info("Total sprites: %d", len(sprites))

    return tuple(sprites)
