from typing import NamedTuple


class Size(NamedTuple):
    w: int
    h: int


class Point(NamedTuple):
    x: int
    y: int


class Rect(NamedTuple):
    x: int
    y: int
    w: int
    h: int

    def size(self) -> Size:
        return Size(self.x, self.y)

    def position(self) -> Point:
        return Point(self.x, self.y)


def center_in_rect(size: Size, target_rect: Rect) -> Point:
    x = target_rect.x + int((target_rect.w - size.w) / 2)
    y = target_rect.y + int((target_rect.h - size.h) / 2)
    return Point(x, y)
