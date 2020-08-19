from typing import NamedTuple, Tuple, Optional

import pyxel

from bansoko.graphics import Rect, Point


class Sprite(NamedTuple):
    image_bank: int
    rect_uv: Rect
    layer_uv: Optional[Tuple[Point]] = None

    def draw(self, position: Point, layer: int = 0) -> None:
        if self.layer_uv and layer >= len(self.layer_uv):
            return

        rect = Rect(self.layer_uv[layer], self.rect_uv.size) if self.layer_uv else self.rect_uv
        pyxel.blt(position.x, position.y, self.image_bank, rect.x, rect.y, rect.w, rect.h)

    @property
    def width(self) -> int:
        """The width of sprite in pixels."""
        return self.rect_uv.w

    @property
    def height(self) -> int:
        """The height of sprite in pixels."""
        return self.rect_uv.h

    @property
    def num_layers(self) -> int:
        """The number of layers this sprite is made of."""
        return len(self.layer_uv) if self.layer_uv else 1
