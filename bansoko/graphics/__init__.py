from typing import NamedTuple, List


class Size(NamedTuple):
    width: int = 0
    height: int = 0


def max_size(size1: Size, size2: Size) -> Size:
    return Size(max(size1.width, size2.width), max(size1.height, size2.height))


def min_size(size1: Size, size2: Size) -> Size:
    return Size(min(size1.width, size2.width), min(size1.height, size2.height))


class Point(NamedTuple):
    x: int
    y: int


class Rect(NamedTuple):
    x: int
    y: int
    w: int
    h: int

    @property
    def size(self) -> Size:
        return Size(self.x, self.y)

    @property
    def position(self) -> Point:
        return Point(self.x, self.y)


def center_in_rect(size: Size, target_rect: Rect = Rect(0, 0, 256, 256)) -> Point:
    x = target_rect.x + int((target_rect.w - size.width) / 2)
    y = target_rect.y + int((target_rect.h - size.height) / 2)
    return Point(x, y)
