from pathlib import Path

import pyxel

from bansoko.graphics import Rect, Size


def process_sprites(base_dir: str, sprites_data):
    # TODO: What a mess!!
    sprites = []
    packer = SpriteSheetPacker(1, base_dir)

    for sprite_data in sprites_data:
        rect = packer.pack_sprite(sprite_data["image"])
        sprites.append({
            "image_bank": 1,
            "image_rect": [rect.x, rect.y, rect.w, rect.h],
            "multilayer": sprite_data.get("multilayer", False)
        })

    return tuple(sprites)


# TODO: Temporary implementation
class SpriteSheetPacker:
    def __init__(self, image_bank: int, base_dir: str) -> None:
        self.image_bank = image_bank
        self.base_dir = base_dir
        # TODO: Reimplement!
        self.start_y = 0

    def pack_sprite(self, filename: str) -> Rect:
        file_path = Path(self.base_dir).joinpath(filename)
        size = self.__read_image_size(file_path)
        rect = Rect.from_coords(0, self.start_y, size.width, size.height)
        pyxel.image(self.image_bank).load(rect.x, rect.y, file_path)

        self.start_y += size.height

        return rect

    @staticmethod
    def __read_image_size(file_path: Path) -> Size:
        with open(file_path, "rb") as file:
            # TODO: TEMPORARY!! REFACTOR IT!
            file.seek(16)
            read_data = file.read(4)
            width = int.from_bytes(read_data, byteorder='big')
            read_data = file.read(4)
            height = int.from_bytes(read_data, byteorder='big')
            return Size(width, height)
