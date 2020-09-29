"""Module exposing Background type."""
from typing import Optional, NamedTuple, Tuple

import pyxel

from bansoko.graphics import Point
from bansoko.graphics.sprite import Sprite
from bansoko.graphics.tilemap import Tilemap


# TODO: Rename it!
class BackgroundElement(NamedTuple):
    """BackgroundElement is a drawable part of Background.

    It's described by sprite and position to be drawn at."""
    sprite: Sprite
    position: Point

    def draw(self) -> None:
        """Draw background element at its defined position."""
        self.sprite.draw(self.position)


class Background(NamedTuple):
    """Background is a composition of background elements that can be drawn on a screen."""
    background_elements: Tuple[BackgroundElement, ...] = ()
    background_color: Optional[int] = None
    background_tilemap: Optional[Tilemap] = None

    def draw(self) -> None:
        """Draw background with all its elements.

        If background color is specified then screen is cleared with that color first.
        """
        if self.background_color:
            pyxel.cls(self.background_color)
        if self.background_tilemap:
            self.background_tilemap.draw()
        if self.background_elements:
            for element in self.background_elements:
                element.draw()
