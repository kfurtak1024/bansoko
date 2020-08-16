import pyxel

from graphics import Rect, Point


class Sprite:
    def __init__(self, image_bank: int, rect: Rect):
        self.image_bank = image_bank
        self.rect = rect

    def draw(self, position: Point):
        # TODO: Not tested yet!
        pyxel.blt(position.x, position.y, self.image_bank, self.rect.x, self.rect.y, self.rect.w,
                  self.rect.h)
