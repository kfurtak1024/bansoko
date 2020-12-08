"""Module exposing graphic related classes and routines."""
from dataclasses import dataclass
from enum import unique, Enum
from functools import total_ordering
from typing import List, Optional, Tuple, Generator

TILEMAP_WIDTH = 256
TILEMAP_HEIGHT = 256
TILE_SIZE = 8

IMAGE_BANK_WIDTH = 256
IMAGE_BANK_HEIGHT = 256

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 256


@unique
class Direction(Enum):
    """Enumeration representing direction in 2D space.

    In addition to int value identifying direction (direction_index) it also stores the
    movement vector (dx, dy)
    """
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
        """Value indicating whether the direction is horizontal or not."""
        return self in (Direction.LEFT, Direction.RIGHT)

    @property
    def vertical(self) -> bool:
        """Value indicating whether the direction is vertical or not."""
        return self in (Direction.UP, Direction.DOWN)

    @classmethod
    def num_directions(cls) -> int:
        """Number of all defined directions."""
        return len(cls.__members__)

    @property
    def opposite(self) -> "Direction":
        """The opposite direction to given direction."""
        if self == Direction.UP:
            return Direction.DOWN
        if self == Direction.DOWN:
            return Direction.UP
        if self == Direction.LEFT:
            return Direction.RIGHT
        if self == Direction.RIGHT:
            return Direction.LEFT

        raise Exception(f"Direction {str(self)} is not supported")


@dataclass(frozen=True)
class Point:
    """A point representing a location in (x, y) screen space."""
    x: int
    y: int

    @classmethod
    def from_list(cls, coords: List[int]) -> "Point":
        """Create a Point from the list of coordinates."""
        return cls(x=coords[0], y=coords[1])

    @property
    def as_list(self) -> List[int]:
        """Point represented as a list containing [x, y]."""
        return [self.x, self.y]

    def offset(self, offset: "Point") -> "Point":
        """Create a new Point which is the result of moving this Point by (x, y)."""
        return Point(self.x + offset.x, self.y + offset.y)

    def move(self, direction: Direction) -> "Point":
        """Create a new Point which is the result of moving this Point in given direction."""
        return Point(self.x + direction.dx, self.y + direction.dy)


@total_ordering
@dataclass(frozen=True)
class Size:
    """Size describes width and height dimensions in pixels."""
    width: int = 0
    height: int = 0

    def enlarge(self, dx: int, dy: Optional[int] = None) -> "Size":
        """Create a new Size enlarged by (dx, dy)"""
        return Size(self.width + dx, self.height + (dy if dy else dx))

    @property
    def max_dimension(self) -> int:
        """Maximum dimension (which is either width or height)"""
        return max(self.width, self.height)

    def can_fit(self, size: "Size") -> bool:
        """Test if given size will fit in this size. Size "fits" in another size only if both width
        and height are less or equal to the size the test is performed against to.
        """
        return self.width >= size.width and self.height >= size.height

    def __lt__(self, other: Tuple[int, ...]) -> bool:
        return (self.width, self.height) < (other[0], other[1])


def max_size(size1: Size, size2: Size) -> Size:
    """Create size with maximum width and height of two given sizes."""
    return Size(max(size1.width, size2.width), max(size1.height, size2.height))


def min_size(size1: Size, size2: Size) -> Size:
    """Create size with minimum width and height of two given sizes."""
    return Size(min(size1.width, size2.width), min(size1.height, size2.height))


SCREEN_RECT = Size(SCREEN_WIDTH, SCREEN_HEIGHT)


@dataclass(frozen=True)
class Rect:
    """A rectangle represented by position and size.

    Position and size can be accessed directly. Use left, right, top, bottom the get the
    coordinates of rectangle 4 edges.
    """
    position: Point
    size: Size

    @classmethod
    def from_coords(cls, x: int, y: int, w: int, h: int) -> "Rect":
        """Create a new Rect with given position (x, y) and size (w, h)"""
        return cls(position=Point(x, y), size=Size(w, h))

    @classmethod
    def from_list(cls, coords: List[int]) -> "Rect":
        """Create a new Rect from the list containing coordinates and size."""
        return cls(position=Point(coords[0], coords[1]), size=Size(coords[2], coords[3]))

    @classmethod
    def from_size(cls, size: Size) -> "Rect":
        """Create a new Rect with given size and positioned at (0, 0)."""
        return cls(position=Point(0, 0), size=size)

    @property
    def as_list(self) -> List[int]:
        """Rect represented as a list containing [x, y, w, h]."""
        return [self.position.x, self.position.y, self.size.width, self.size.height]

    @property
    def x(self) -> int:
        """The x coordinate of the rect."""
        return self.position.x

    @property
    def y(self) -> int:
        """The y coordinate of the rect."""
        return self.position.y

    @property
    def w(self) -> int:
        """The width of the rect."""
        return self.size.width

    @property
    def h(self) -> int:
        """The height of the rect."""
        return self.size.height

    @property
    def left(self) -> int:
        """The position of left edge of the rect."""
        return self.x

    @property
    def right(self) -> int:
        """The position of right edge of the rect."""
        return self.x + self.w - 1

    @property
    def top(self) -> int:
        """The position of top edge of the rect."""
        return self.y

    @property
    def bottom(self) -> int:
        """The position of bottom edge of the rect."""
        return self.y + self.h - 1

    def offset(self, delta: Point) -> "Rect":
        """Create a new Rect which is the result of moving this Rect by (dx, dy)."""
        return Rect(self.position.offset(delta), self.size)

    def enlarge(self, w: int, h: int) -> "Rect":
        """Create a new Rect enlarged with given size (w, h)."""
        return Rect(position=self.position, size=self.size.enlarge(w, h))

    def inside_points(self) -> Generator[Point, None, None]:
        """Generator for iterating over all valid positions inside the rectangle (from top-left to
        bottom-right)."""
        for y in range(self.y, self.y + self.h):
            for x in range(self.x, self.x + self.w):
                yield Point(x, y)


def hcenter(width: int, target_x: int, target_width: int = SCREEN_WIDTH) -> int:
    """Center horizontally 'size' with specified width in a target section (described by x and
    width)."""
    return target_x + (target_width - width) // 2


def vcenter(height: int, target_y: int, target_height: int = SCREEN_HEIGHT) -> int:
    """Center vertically 'size' with specified height in a target section (described by y and
    height)."""
    return hcenter(height, target_y, target_height)


def center_in_rect(size: Size, target_rect: Rect = Rect.from_size(SCREEN_RECT)) -> Rect:
    """Return rectangle with given size centered in target rectangle."""
    x = hcenter(size.width, target_rect.x, target_rect.w)
    y = vcenter(size.height, target_rect.y, target_rect.h)
    return Rect(Point(x, y), size)


@dataclass(frozen=True)
class Layer:
    """Layer is an abstract surface on which elements can be drawn.

    Layers are used when drawing elements that should be put on each other in order to achieve
    pseudo 3d effect.

    Attributes:
        layer_index - index of the layer (used to calculate layer offset)
        opaque - is layer opaque *OR* transparent
        global_offset - offset of elements drawn on the layer
    """
    layer_index: int
    opaque: bool = False
    global_offset: Point = Point(0, 0)

    @property
    def offset(self) -> Point:
        """Position offset for all graphical objects drawn on this layer."""
        return self.global_offset.offset(Point(-self.layer_index, -self.layer_index))

    @property
    def transparency_color(self) -> int:
        """Transparency color for the layer."""
        return -1 if self.opaque else 0
