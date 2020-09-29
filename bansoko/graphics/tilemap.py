from typing import NamedTuple, Any, Generator, Optional

import pyxel

from bansoko.graphics import Rect, Direction, Point, Layer

TILE_SIZE = 8


class TilePosition(NamedTuple):
    tile_x: int = 0
    tile_y: int = 0

    def move(self, direction: Direction) -> "TilePosition":
        return TilePosition(self.tile_x + direction.dx, self.tile_y + direction.dy)

    def to_point(self) -> Point:
        return Point(self.tile_x * TILE_SIZE, self.tile_y * TILE_SIZE)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TilePosition):
            return self.tile_x == other.tile_x and self.tile_y == other.tile_y
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.tile_x, self.tile_y))


class Tilemap(NamedTuple):
    tilemap_id: int
    rect_uv: Rect
    num_layers: int = 1

    @property
    def width(self) -> int:
        return self.rect_uv.w

    @property
    def height(self) -> int:
        return self.rect_uv.h

    def tile_index_at(self, position: TilePosition) -> int:
        tile_index: int = pyxel.tilemap(self.tilemap_id).get(
            self.rect_uv.x + position.tile_x, self.rect_uv.y + position.tile_y)
        return tile_index

    def tiles_positions(self) -> Generator[TilePosition, None, None]:
        for i in range(self.width * self.height):
            yield TilePosition(i % self.width, i // self.width)

    def draw(self, layer: Layer = Layer(0)) -> None:
        if layer and layer.layer_index >= self.num_layers:
            return

        pyxel.bltm(layer.offset.x, layer.offset.y, self.tilemap_id + layer.layer_index,
                   self.rect_uv.x, self.rect_uv.y, self.rect_uv.w, self.rect_uv.h,
                   colkey=-1 if layer.layer_index == 0 else 0)  # TODO: Layer should have information about transparent color!
