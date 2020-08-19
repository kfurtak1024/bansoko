from typing import Optional, NamedTuple, Tuple

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
    background_elements: Optional[Tuple[BackgroundElement, ...]] = None
    background_color: Optional[int] = None

    def draw(self) -> None:
        if self.background_color:
            pyxel.cls(self.background_color)
        if self.background_elements:
            for element in self.background_elements:
                element.draw()
