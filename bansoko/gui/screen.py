"""Module exposing GUI elements like screen, image and text."""
from dataclasses import dataclass

import pyxel

from bansoko.graphics import Point, Layer, Rect
from bansoko.graphics.sprite import Sprite
from bansoko.graphics.text import draw_text
from bansoko.graphics.tilemap import Tilemap


@dataclass(frozen=True)
class ScreenElement:
    """ScreenElement is a drawable part of Screen.

    It's described by sprite *OR* text and by position to be drawn at.
    """
    position: Point
    sprite: Sprite | None = None
    text: str | None = None

    def draw(self) -> None:
        """Draw screen element at its defined position."""
        if self.sprite:
            self.sprite.draw(self.position)
        elif self.text:
            draw_text(self.position, self.text)


@dataclass(frozen=True)
class Screen:
    """Screen is a composition of elements that can be drawn on a game screen."""
    background_color: int | None = None
    background_tilemap: Tilemap | None = None
    elements: tuple[ScreenElement, ...] = ()
    menu_position: Point | None = None
    menu_scrollbar_rect: Rect | None = None

    def draw(self) -> None:
        """Draw screen with all its elements.

        If background color is specified then screen is cleared with that color first.
        """
        if self.background_color is not None:
            pyxel.cls(self.background_color)
        if self.background_tilemap:
            self.background_tilemap.draw(Layer(0))
        if self.elements:
            for element in self.elements:
                element.draw()
