import logging
from collections import deque
from pathlib import Path
from typing import NamedTuple, List, Optional

import pyxel

from bansoko.graphics import Rect, Size


# TODO: Clean up class names in this module!!


class BoxPackerNode:
    def __init__(self, rect: Rect) -> None:
        self.box_id: Optional[int] = None
        self.rect: Rect = rect
        self.right_child: Optional[BoxPackerNode] = None
        self.bottom_child: Optional[BoxPackerNode] = None

    def split(self, right: int, bottom: int) -> None:
        if self.is_split:
            return

        self.bottom_child = BoxPackerNode(Rect.from_coords(
            self.rect.x, self.rect.y + bottom,
            self.rect.w, self.rect.h - bottom))
        self.right_child = BoxPackerNode(Rect.from_coords(
            self.rect.x + right, self.rect.y,
            self.rect.w - right, bottom))
        self.rect = Rect(self.rect.position, Size(right, bottom))

    @staticmethod
    def find_node_for_box(root_node: "BoxPackerNode", box_size: Size) -> Optional["BoxPackerNode"]:
        node_deque = deque([root_node])

        while node_deque:
            node = node_deque.popleft()
            if node.has_box and node.is_split:
                node_deque.appendleft(node.bottom_child)
                node_deque.appendleft(node.right_child)
            elif node.rect.size.can_fit(box_size):
                return node

        return None

    @property
    def has_box(self) -> bool:
        return self.box_id is not None

    @property
    def is_split(self) -> bool:
        return self.right_child is not None and self.bottom_child is not None


class Box(NamedTuple):
    id: int
    size: Size


class BoxPacker:
    def __init__(self) -> None:
        self.boxes: List[Box] = []

    def add_box(self, box_size: Size) -> int:
        box = Box(len(self.boxes), box_size)
        self.boxes.append(box)
        return box.id

    def pack(self, size: Size) -> List[Rect]:
        if not self.boxes:
            return []

        uv_rects: List[Rect] = [Rect.from_coords(0, 0, 0, 0)] * len(self.boxes)
        sorted_boxes = sorted(self.boxes, key=lambda b: b.size.max_dimension, reverse=True)
        root_node = BoxPackerNode(Rect.from_size(size))

        for box in sorted_boxes:
            node = BoxPackerNode.find_node_for_box(root_node, box.size)
            if node:
                node.split(box.size.width, box.size.height)
                node.box_id = box.id
                uv_rects[box.id] = node.rect
            else:
                raise Exception(f"Unable to fit box with size ({box.size.width}x{box.size.height})")

        return uv_rects


class SpriteSheetPacker:
    def __init__(self) -> None:
        self.box_packer = BoxPacker()
        self.sprite_paths: List[Path] = []

    def add_sprite(self, sprite_path: Path) -> int:
        self.sprite_paths.append(sprite_path)
        sprite_size = self.read_png_image_size(sprite_path)
        return self.box_packer.add_box(sprite_size)

    def pack(self, image_bank: int, size: Size) -> List[Rect]:
        uv_rects = self.box_packer.pack(size)
        for i, rect in enumerate(uv_rects):
            pyxel.image(image_bank).load(rect.x, rect.y, str(self.sprite_paths[i]))

        return uv_rects

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


def process_sprites(base_dir: Path, sprites_data):
    packer = SpriteSheetPacker()
    image_bank = 1  # TODO: Hard-coded image bank

    sprites = {}
    sprites_ids = {}

    for sprite_name, sprite_data in sprites_data.items():
        sprite_path = Path(base_dir).joinpath(sprite_data["image"])
        sprites_ids[sprite_name] = packer.add_sprite(sprite_path)

        # TODO: 3 should be configurable
        num_layers = 3 if sprite_data.get("multilayer", False) else 1

        sprites[sprite_name] = {
            "image_bank": image_bank,
            "directional": sprite_data.get("directional", False),
            "num_frames": sprite_data.get("num_frames", 1),
            "num_layers": num_layers
        }

    sprite_uv_rects = packer.pack(image_bank, Size(256, 256))

    for sprite_name, sprite in sprites.items():
        uv_rect = sprite_uv_rects[sprites_ids[sprite_name]]
        sprite["uv_rect"] = uv_rect.as_list
        logging.info("Sprite '%s' (%dx%d) added to image bank %d", sprite_name,
                     uv_rect.w, uv_rect.h, image_bank)

    logging.info("Total sprites: %d", len(sprites))

    return sprites
