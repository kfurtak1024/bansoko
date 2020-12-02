"""Module for handling tilemaps."""
from dataclasses import dataclass
from typing import Generator

import pyxel

from bansoko.graphics import Rect, Direction, Point, Layer, TILE_SIZE


@dataclass(frozen=True)
class TilePosition:
    """Position of tile in tilemap space."""
    tile_x: int = 0
    tile_y: int = 0

    def move(self, direction: Direction) -> "TilePosition":
        """Create tile position that is a result of moving this tile position in specified
        direction by one tile.

        :param direction: direction to move tile position in
        :return: newly created tile position
        """
        return TilePosition(self.tile_x + direction.dx, self.tile_y + direction.dy)

    def to_point(self) -> Point:
        """Convert tile position to a point in screen space."""
        return Point(self.tile_x * TILE_SIZE, self.tile_y * TILE_SIZE)


@dataclass(frozen=True)
class Tilemap:
    """Tilemap is a rectangular fragment of Pyxel's mega-tilemap and describes the level layout.

    Tilemaps can have multiple layers (to achieve pseudo 3d effect). In that case all layers are
    stored on separate Pyxel's mega-tilemaps. For example: tilemap with 3 layers is defined across
    Pyxel's mega-tilemaps: tilemap_id, tilemap_id+1 and tilemap_id+2.

    Attributes:
        tilemap_id - Pyxel's mega-tilemap id
        rect_uv    - coordinates of the tilemap in Pyxel's mega-tilemap (Tilemap is just a fragment
                     of Pyxel's mega-tilemap)
        num_layers - number of layers the tilemap consists of (each layer is stored in a separate
                     Pyxel's mega-tilemap)
    """
    tilemap_id: int
    rect_uv: Rect
    num_layers: int = 1

    @property
    def width(self) -> int:
        """Width of the tilemap (expressed as a number of horizontal tiles)."""
        return self.rect_uv.w

    @property
    def height(self) -> int:
        """Height of the tilemap (expressed as a number of vertical tiles)."""
        return self.rect_uv.h

    def tile_index_at(self, position: TilePosition) -> int:
        """Return index of tile at specified position.

        :param position: tile position to retrieve tile index at
        :return: index of tile at given position
        """
        tile_index: int = pyxel.tilemap(self.tilemap_id).get(
            self.rect_uv.x + position.tile_x, self.rect_uv.y + position.tile_y)
        return tile_index

    def tiles_positions(self) -> Generator[TilePosition, None, None]:
        """Generator for iterating over all valid tile positions for this tilemap."""
        for i in range(self.width * self.height):
            yield TilePosition(i % self.width, i // self.width)

    def draw(self, layer: Layer) -> None:
        """Draw tilemap on given layer.

        :param layer: layer to draw tilemap on
        """
        if layer and layer.layer_index >= self.num_layers:
            return

        pyxel.bltm(layer.offset.x, layer.offset.y, self.tilemap_id + layer.layer_index,
                   self.rect_uv.x, self.rect_uv.y, self.rect_uv.w, self.rect_uv.h,
                   colkey=layer.transparency_color)
