from typing import NamedTuple, List

import pyxel

from bansoko.graphics import Rect, Point, Direction, Layer


class Sprite(NamedTuple):
    image_bank: int
    rect_uv: Rect
    multilayer: bool = False
    directional: bool = False
    num_frames: int = 1

    def draw(self, position: Point, layer: Layer = Layer.LAYER_0,
             direction: Direction = Direction.UP, frame: int = 0) -> None:
        if not self.multilayer and not layer.is_main:
            return

        clamped_frame = min(frame, self.num_frames - 1)

        x = self.rect_uv.x + clamped_frame * self.rect_uv.w // self.num_frames
        y = self.rect_uv.y

        if self.directional:
            x += self.rect_uv.w // Direction.num_directions() * direction.direction_index

        if self.multilayer:
            top_layer = Layer.LAYER_2.layer_index
            x += top_layer + layer.offset.x
            y += top_layer + layer.offset.y

        pyxel.blt(position.x + layer.offset.x, position.y + layer.offset.y, self.image_bank, x,
                  y, self.width, self.height, 0)

    @property
    def width(self) -> int:
        """The width of sprite in pixels."""
        width = self.rect_uv.w // self.num_frames

        if self.directional:
            width //= Direction.num_directions()

        if self.multilayer:
            top_layer = Layer.LAYER_2.layer_index
            width -= top_layer

        return width

    @property
    def height(self) -> int:
        """The height of sprite in pixels."""
        height = self.rect_uv.h

        if self.multilayer:
            top_layer = Layer.LAYER_2.layer_index
            height -= top_layer

        return height


class SkinPack(NamedTuple):
    skin_sprites: List[Sprite]

    def get_sprite(self, sprite_index: int) -> Sprite:
        return self.skin_sprites[sprite_index]
