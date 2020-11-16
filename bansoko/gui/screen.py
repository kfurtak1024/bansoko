"""Module exposing GUI elements like screen, image and text."""
from dataclasses import dataclass
from typing import Optional, Tuple

import pyxel

from bansoko.graphics import Point, Layer
from bansoko.graphics.sprite import Sprite
from bansoko.graphics.tilemap import Tilemap


@dataclass(frozen=True)
class ScreenElement:
    """ScreenElement is a drawable part of Screen.

    It's described by sprite and position to be drawn at.
    """
    sprite: Sprite
    position: Point

    def draw(self) -> None:
        """Draw screen element at its defined position."""
        self.sprite.draw(self.position)


@dataclass(frozen=True)
class Screen:
    """Screen is a composition of elements that can be drawn on a game screen."""
    elements: Tuple[ScreenElement, ...] = ()
    background_color: Optional[int] = None
    background_tilemap: Optional[Tilemap] = None

    def draw(self) -> None:
        """Draw screen with all its elements.

        If background color is specified then screen is cleared with that color first.
        """
        if self.background_color:
            pyxel.cls(self.background_color)
        if self.background_tilemap:
            self.background_tilemap.draw(Layer(0))
        if self.elements:
            for element in self.elements:
                element.draw()
