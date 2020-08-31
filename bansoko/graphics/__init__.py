from enum import unique, Enum
from functools import total_ordering
from typing import NamedTuple, List, Any, Optional, Tuple


@unique
class Direction(Enum):
    UP = 0, (0, -1)
    DOWN = 1, (0, 1)
    LEFT = 2, (-1, 0)
    RIGHT = 3, (1, 0)

    def __init__(self, direction_index: int, delta: Tuple[int, int]) -> None:
        self.direction_index = direction_index
        self.dx = delta[0]
        self.dy = delta[1]

    @property
    def horizontal(self) -> bool:
        return self in (Direction.LEFT, Direction.RIGHT)

    @property
    def vertical(self) -> bool:
        return self in (Direction.UP, Direction.DOWN)

    @classmethod
    def num_directions(cls) -> int:
        return len(cls.__members__)

    @property
    def opposite(self) -> "Direction":
        if self == Direction.UP:
            return Direction.DOWN
        if self == Direction.DOWN:
            return Direction.UP
        if self == Direction.LEFT:
            return Direction.RIGHT
        if self == Direction.RIGHT:
            return Direction.LEFT


class Point(NamedTuple):
    x: int
    y: int

    @classmethod
    def from_list(cls, coords: List[int]) -> "Point":
        return cls(x=coords[0], y=coords[1])

    def offset(self, dx: int, dy: int) -> "Point":
        return Point(self.x + dx, self.y + dy)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.x, self.y))


@total_ordering
class Size(NamedTuple):
    width: int = 0
    height: int = 0

    def enlarge(self, dx: int, dy: Optional[int] = None) -> "Size":
        return Size(self.width + dx, self.height + (dy if dy else dx))

    @property
    def max_dimension(self) -> int:
        return max(self.width, self.height)

    def can_fit(self, size: "Size") -> bool:
        return self.width >= size.width and self.height >= size.height

    def __lt__(self, other: Tuple[int, ...]) -> bool:
        return (self.width, self.height) < (other[0], other[1])

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Size):
            return self.width == other.width and self.height == other.height
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.width, self.height))


def max_size(size1: Size, size2: Size) -> Size:
    return Size(max(size1.width, size2.width), max(size1.height, size2.height))


def min_size(size1: Size, size2: Size) -> Size:
    return Size(min(size1.width, size2.width), min(size1.height, size2.height))


class Rect(NamedTuple):
    position: Point
    size: Size

    @classmethod
    def from_coords(cls, x: int, y: int, w: int, h: int) -> "Rect":
        return cls(position=Point(x, y), size=Size(w, h))

    @classmethod
    def from_list(cls, coords: List[int]) -> "Rect":
        return cls(position=Point(coords[0], coords[1]), size=Size(coords[2], coords[3]))

    @classmethod
    def from_size(cls, size: Size) -> "Rect":
        return cls(position=Point(0, 0), size=size)

    @property
    def as_list(self) -> List[int]:
        return [self.position.x, self.position.y, self.size.width, self.size.height]

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

    @property
    def left(self) -> int:
        return self.x

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def top(self) -> int:
        return self.y

    @property
    def bottom(self) -> int:
        return self.y + self.h

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Rect):
            return self.position == other.position and self.size == other.size
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.position, self.size))


def center_in_rect(size: Size, target_rect: Rect = Rect.from_coords(0, 0, 256, 256)) -> Point:
    x = target_rect.x + int((target_rect.w - size.width) / 2)
    y = target_rect.y + int((target_rect.h - size.height) / 2)
    return Point(x, y)


@unique
class Layer(Enum):
    LAYER_0 = 0, Point(0, 0)
    LAYER_1 = 1, Point(-1, -1)
    LAYER_2 = 2, Point(-2, -2)

    def __init__(self, layer_index: int, offset: Point):
        self.layer_index = layer_index
        self.offset = offset

    @property
    def is_main(self) -> bool:
        return self == Layer.LAYER_0

    @property
    def top_layer(self) -> int:
        return Layer.LAYER_2.layer_index
