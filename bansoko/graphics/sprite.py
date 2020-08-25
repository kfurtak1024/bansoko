from typing import NamedTuple

import pyxel

from bansoko.graphics import Rect, Point, Direction, Layer


class Sprite(NamedTuple):
    image_bank: int
    rect_uv: Rect
    multilayer: bool = False
    directional: bool = False

    def draw(self, position: Point, layer: Layer = Layer.LAYER_0,
             direction: Direction = Direction.UP) -> None:
        if not self.multilayer and not layer.is_main:
            return

        x = self.rect_uv.x
        y = self.rect_uv.y
        w = self.rect_uv.w
        h = self.rect_uv.h

        if self.directional:
            w //= Direction.num_directions()
            x = w * direction.direction_index

        if self.multilayer:
            top_layer = Layer.LAYER_2.layer_index
            x += top_layer + layer.offset.x
            y += top_layer + layer.offset.y
            w -= top_layer
            h -= top_layer

        rect = Rect.from_coords(x, y, w, h)
        pyxel.blt(position.x + layer.offset.x, position.y + layer.offset.y, self.image_bank, rect.x,
                  rect.y, rect.w, rect.h, 0)

    @property
    def width(self) -> int:
        """The width of sprite in pixels."""
        return self.rect_uv.w  # TODO: Not true anymore (take directional and multilayer into account)

    @property
    def height(self) -> int:
        """The height of sprite in pixels."""
        return self.rect_uv.h - 2 if self.multilayer else self.rect_uv.h
