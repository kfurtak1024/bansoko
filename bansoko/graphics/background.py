from typing import List

from graphics import Point
from graphics.sprite import Sprite


class BackgroundElement:
    def __init__(self, sprite: Sprite, position: Point):
        self.sprite = sprite
        self.position = position

    def draw(self):
        self.sprite.draw(self.position)


class Background:
    def __init__(self, background_elements: List[BackgroundElement]):
        self.background_elements = background_elements

    def draw(self):
        for background_element in self.background_elements:
            background_element.draw()
