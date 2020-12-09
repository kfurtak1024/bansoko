"""Module for processing and packing sprites."""
import logging
from pathlib import Path
from typing import List, Dict, Any

import pyxel

from bansoko import LEVEL_NUM_LAYERS
from bansoko.graphics import Rect, Size, IMAGE_BANK_HEIGHT, IMAGE_BANK_WIDTH
from resbuilder import ResourceError
from resbuilder.resources.box_packer import BoxPacker

PNG_HEADER = "89 50 4E 47 0D 0A 1A 0A"
PNG_CHUNK_TYPE = b"IHDR"


class SpriteSheetPacker:
    """Packer for packing sprites into a sprite sheet using BoxPacker.

    Attributes:
        image_bank - destination Pyxel's image bank
        rect - destination sprite sheet's rect to pack sprites in
    """

    def __init__(self, image_bank: int, rect: Rect) -> None:
        self.box_packer = BoxPacker()
        self.sprite_paths: List[Path] = []
        self.image_bank = image_bank
        self.rect = rect

    def add_sprite(self, sprite_path: Path) -> int:
        """Add sprite to collection of sprites that will be packed during pack() call.

        :param sprite_path: location of sprite image file
        :return: id assigned to given sprite (look at pack())
        """
        self.sprite_paths.append(sprite_path)
        sprite_size = self.read_png_image_size(sprite_path)
        return self.box_packer.add_box(sprite_size)

    def pack(self) -> List[Rect]:
        """Pack all sprites that were added to sprite sheet packer.

        :return: collection of texture coordinates for all packed sprites (coords for given sprite
                 can be found by using sprite's id assigned during add_sprite call)
        """
        uv_rects = self.box_packer.pack(self.rect)
        for i, rect in enumerate(uv_rects):
            pyxel.image(self.image_bank).load(rect.x, rect.y, str(self.sprite_paths[i]))

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
    sprite_packers = [
        SpriteSheetPacker(0, Rect.from_coords(0, 128, IMAGE_BANK_WIDTH, IMAGE_BANK_HEIGHT - 128)),
        SpriteSheetPacker(1, Rect.from_coords(0, 0, IMAGE_BANK_WIDTH, IMAGE_BANK_HEIGHT))]
    sprites = {}
    sprites_ids: List[Dict[str, int]] = [{}, {}]

    for sprite_name, sprite_data in input_data.items():
        image_bank = sprite_data["image_bank"]
        sprite_path = Path(base_dir).joinpath(sprite_data["image"])
        sprites_ids[image_bank][sprite_name] = sprite_packers[image_bank].add_sprite(sprite_path)
        num_layers = LEVEL_NUM_LAYERS if sprite_data.get("multilayer", False) else 1
        transparency_color = -1
        if sprite_data.get("transparency_color"):
            transparency_color = int(sprite_data["transparency_color"], 16)

        sprites[sprite_name] = {
            "image_bank": image_bank,
            "directional": sprite_data.get("directional", False),
            "transparency_color": transparency_color,
            "num_frames": sprite_data.get("num_frames", 1),
            "num_layers": num_layers
        }

    sprite_uv_rects = [packer.pack() for packer in sprite_packers]

    for sprite_name, sprite in sprites.items():
        image_bank = sprite["image_bank"]
        sprite_id = sprites_ids[image_bank][sprite_name]
        uv_rect = sprite_uv_rects[image_bank][sprite_id]
        sprite["uv_rect"] = uv_rect.as_list
        logging.info("Sprite '%s' (%dx%d) added to image bank %d", sprite_name,
                     uv_rect.w, uv_rect.h, image_bank)

    logging.info("Total sprites: %d", len(sprites))
    return sprites
