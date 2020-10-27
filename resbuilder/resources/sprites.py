"""Module for processing and packing sprites."""
import logging
from pathlib import Path
from typing import List, Dict, Any

import pyxel

from bansoko import IMAGE_BANK_HEIGHT, IMAGE_BANK_WIDTH, LEVEL_NUM_LAYERS, SPRITE_IMAGE_BANK
from bansoko.graphics import Rect, Size
from resbuilder import ResourceError
from resbuilder.resources.box_packer import BoxPacker

PNG_HEADER = "89 50 4E 47 0D 0A 1A 0A"
PNG_CHUNK_TYPE = b"IHDR"


class SpriteSheetPacker:
    """Packer for packing sprites into a sprite sheet using BoxPacker."""
    def __init__(self) -> None:
        self.box_packer = BoxPacker()
        self.sprite_paths: List[Path] = []

    def add_sprite(self, sprite_path: Path) -> int:
        """Add sprite to collection of sprites that will be packed during pack() call.

        :param sprite_path: location of sprite image file
        :return: id assigned to given sprite (look at pack())
        """
        self.sprite_paths.append(sprite_path)
        sprite_size = self.read_png_image_size(sprite_path)
        return self.box_packer.add_box(sprite_size)

    def pack(self, image_bank: int, size: Size) -> List[Rect]:
        """Pack all sprites that were added to sprite sheet packer.

        :param image_bank: destination Pyxel's image bank
        :param size: destination sprite sheet's size to pack sprites in
        :return: collection of texture coordinates for all packed sprites (coords for given sprite
                 can be found by using sprite's id assigned during add_sprite call)
        """
        uv_rects = self.box_packer.pack(size)
        for i, rect in enumerate(uv_rects):
            pyxel.image(image_bank).load(rect.x, rect.y, str(self.sprite_paths[i]))

        return uv_rects

    @staticmethod
    def read_png_image_size(file_path: Path) -> Size:
        """Read size of given PNG image file.

        :param file_path: path to PNG file we are retrieving image size for
        :return: size of given PNG image
        """
        with open(file_path, "rb") as file:
            header = file.read(8)
            if header != bytes.fromhex(PNG_HEADER):
                raise ResourceError(f"File '{file_path}' is not a valid PNG file")
            file.read(4)
            chunk_type = file.read(4)
            if chunk_type != PNG_CHUNK_TYPE:
                raise ResourceError(f"File '{file_path}' is not a valid PNG file")

            width = int.from_bytes(file.read(4), byteorder='big')
            height = int.from_bytes(file.read(4), byteorder='big')
            return Size(width, height)


def process_sprites(input_data: Dict[str, Any], base_dir: Path) -> Dict[str, Any]:
    """Process and pack sprites from input resource file into sprite sheet.

    :param input_data: input data from JSON file (root -> sprites)
    :param base_dir:
    :return: processed sprites (ready to be serialized to JSON)
    """
    packer = SpriteSheetPacker()
    image_bank = SPRITE_IMAGE_BANK

    sprites = {}
    sprites_ids = {}

    for sprite_name, sprite_data in input_data.items():
        sprite_path = Path(base_dir).joinpath(sprite_data["image"])
        sprites_ids[sprite_name] = packer.add_sprite(sprite_path)
        num_layers = LEVEL_NUM_LAYERS if sprite_data.get("multilayer", False) else 1

        sprites[sprite_name] = {
            "image_bank": image_bank,
            "directional": sprite_data.get("directional", False),
            "num_frames": sprite_data.get("num_frames", 1),
            "num_layers": num_layers
        }

    sprite_uv_rects = packer.pack(image_bank, Size(IMAGE_BANK_WIDTH, IMAGE_BANK_HEIGHT))

    for sprite_name, sprite in sprites.items():
        uv_rect = sprite_uv_rects[sprites_ids[sprite_name]]
        sprite["uv_rect"] = uv_rect.as_list
        logging.info("Sprite '%s' (%dx%d) added to image bank %d", sprite_name,
                     uv_rect.w, uv_rect.h, image_bank)

    logging.info("Total sprites: %d", len(sprites))
    return sprites
