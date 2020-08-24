from typing import NamedTuple, Tuple, Optional

import pyxel

from bansoko.graphics import Rect, Point, Size


class Sprite(NamedTuple):
    image_bank: int
    rect_uv: Rect
    multilayer: bool = False

    def draw(self, position: Point, layer: int = 0) -> None:
        # TODO: Hard-coded 2!

        if self.multilayer:
            rect = Rect(
                Point(self.rect_uv.x + (2 - layer), self.rect_uv.y + (2 - layer)),
                Size(self.rect_uv.w - 2, self.rect_uv.h - 2))
        else:
            rect = self.rect_uv

        # TODO: What about transparency?
        pyxel.blt(position.x, position.y, self.image_bank, rect.x, rect.y, rect.w, rect.h, 0)

    @property
    def width(self) -> int:
        """The width of sprite in pixels."""
        return self.rect_uv.w

    @property
    def height(self) -> int:
        """The height of sprite in pixels."""
        return self.rect_uv.h
