from typing import List, Optional, NamedTuple

import pyxel

from bansoko.graphics import Point
from bansoko.graphics.sprite import Sprite


class BackgroundElement(NamedTuple):
    sprite: Sprite
    position: Point

    def draw(self) -> None:
        """Draw background elements at its defined position."""
        self.sprite.draw(self.position)


class Background(NamedTuple):
    background_elements: Optional[List[BackgroundElement]] = None
    background_color: Optional[int] = None

    def draw(self) -> None:
        if self.background_color is not None:
            pyxel.cls(self.background_color)
        if self.background_elements is not None:
            for element in self.background_elements:
                element.draw()
