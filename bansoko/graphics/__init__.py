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

    @classmethod
    def from_list(cls, coords: List[int]):
        return cls(x=coords[0], y=coords[1])


class Rect(NamedTuple):
    position: Point
    size: Size

    @classmethod
    def from_coords(cls, x: int, y: int, w: int, h: int):
        return cls(position=Point(x, y), size=Size(w, h))

    @classmethod
    def from_list(cls, coords: List[int]):
        return cls(position=Point(coords[0], coords[1]), size=Size(coords[2], coords[3]))

    @property
    def x(self) -> int:
        return self.position.x

    @property
    def y(self) -> int:
        return self.position.y

    @property
    def w(self) -> int:
        return self.size.width

    @property
    def h(self) -> int:
        return self.size.height


def center_in_rect(size: Size, target_rect: Rect = Rect.from_coords(0, 0, 256, 256)) -> Point:
    x = target_rect.x + int((target_rect.w - size.width) / 2)
    y = target_rect.y + int((target_rect.h - size.height) / 2)
    return Point(x, y)
