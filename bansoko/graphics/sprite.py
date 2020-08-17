from typing import NamedTuple

import pyxel

from bansoko.graphics import Rect, Point


class Sprite(NamedTuple):
    image_bank: int
    image_rect: Rect

    def draw(self, position: Point):
        pyxel.blt(position.x, position.y, self.image_bank, self.image_rect.x, self.image_rect.y,
                  self.image_rect.w, self.image_rect.h)
