from typing import NamedTuple

import pyxel

from bansoko.graphics import Rect, Point


class Sprite(NamedTuple):
    image_bank: int
    image_rect: Rect

    def draw(self, position: Point) -> None:
        """
        Draw sprite at given position.

        Arguments:
            position - position to draw sprite at
        """
        pyxel.blt(position.x, position.y, self.image_bank, self.image_rect.x, self.image_rect.y,
                  self.image_rect.w, self.image_rect.h)

    @property
    def width(self) -> int:
        """The width of sprite in pixels."""
        return self.image_rect.w

    @property
    def height(self) -> int:
        """The height of sprite in pixels."""
        return self.image_rect.h
