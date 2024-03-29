"""Module for processing tilemap generators (that can be used in backgrounds)."""
import logging
import random
from dataclasses import dataclass
from enum import Enum, unique
from typing import Dict, Any, Tuple

import pyxel

from bansoko.graphics import Rect
from resbuilder.resources.tiles import TilePacker


@dataclass(frozen=True)
class TilemapGenerator:
    """Generator for generating randomized tilemaps.

    Every tile has relative weight used during randomization.
    """
    tiles_weights: Dict[Tuple[int, int], int]

    def generate_tilemap(self, tilemap_id: int, tilemap_rect: Rect, seed: int) -> None:
        """Generate a tilemap using random tiles at given position in Pyxel's mega-tilemap.

        Tiles are randomized using specified seed and tiles weights.

        :param tilemap_id: Pyxel's mega-tilemap id
        :param tilemap_rect: tilemap rect where generated tiles will be put into
        :param seed: seed to be used during tiles generation
        """
        state = random.getstate()
        random.seed(seed)
        tilemap_points = tilemap_rect.inside_points()
        for point in tilemap_points:
            pyxel.tilemap(tilemap_id).pset(point.x, point.y, self._next_tile())
        random.setstate(state)

    def _next_tile(self) -> Tuple[int, int]:
        if not self.tiles_weights:
            return 0, 0
        return random.choices(list(self.tiles_weights.keys()),
                              list(self.tiles_weights.values())).pop()


def process_tilemap_generators(input_data: Any, tile_packer: TilePacker) \
        -> Dict[str, TilemapGenerator]:
    """Process tilemap generators from input resource file.

    :param input_data: input data from JSON file (root -> tilemap_generators)
    :param tile_packer: tile packer used to pack tiles generated by tilemap generator
    :return: processed tilemap generators (ready to be serialized to JSON)
    """
    generators: Dict[str, TilemapGenerator] = {}

    for generator_name, generator_data in input_data.items():
        tiles_weights = {}
        for tile_filename, tile_probability in generator_data.items():
            tile_id = tile_packer.pack_tile(tile_filename)
            tiles_weights[tile_id] = tile_probability

        generators[generator_name] = TilemapGenerator(tiles_weights)
        logging.info("Tilemap generator '%s' added", generator_name)

    logging.info("Total tilemap generators: %d", len(generators))

    return generators


@unique
class FrameSlice(Enum):
    """Types of slices that make NineSlicingFrame."""
    TOP_LEFT_TILE = "top_left"
    TOP_TILE = "top"
    TOP_RIGHT_TILE = "top_right"
    LEFT_TILE = "left"
    CENTER_TILE = "center"
    RIGHT_TILE = "right"
    BOTTOM_LEFT_TILE = "bottom_left"
    BOTTOM_TILE = "bottom"
    BOTTOM_RIGHT_TILE = "bottom_right"


@dataclass(frozen=True)
class NineSlicingFrame:
    """NineSlicingFrame is a frame that can be drawn on a tilemap using collection of 9 slicing
    tiles."""
    slice_tiles: Dict[FrameSlice, Tuple[int, int]]

    def draw_frame(self, tilemap_id: int, rect: Rect) -> None:
        """Draw a frame with nine slicing technique using slice tiles.
        Frame is drawn on given Pyxel's tilemap.

        :param tilemap_id: Pyxel's tilemap id to draw frame on
        :param rect: rectangle describing drawn frame
        """
        tilemap = pyxel.tilemap(tilemap_id)
        tilemap.pset(rect.left, rect.top, self._get_tile(FrameSlice.TOP_LEFT_TILE))
        tilemap.pset(rect.right, rect.top, self._get_tile(FrameSlice.TOP_RIGHT_TILE))
        if rect.bottom > rect.top:
            tilemap.pset(rect.left, rect.bottom, self._get_tile(FrameSlice.BOTTOM_LEFT_TILE))
            tilemap.pset(rect.right, rect.bottom, self._get_tile(FrameSlice.BOTTOM_RIGHT_TILE))

        for x in range(rect.left + 1, rect.right):
            tilemap.pset(x, rect.top, self._get_tile(FrameSlice.TOP_TILE))
            for y in range(rect.top + 1, rect.bottom):
                tilemap.pset(x, y, self._get_tile(FrameSlice.CENTER_TILE))
            if rect.bottom > rect.top:
                tilemap.pset(x, rect.bottom, self._get_tile(FrameSlice.BOTTOM_TILE))

        for y in range(rect.top + 1, rect.bottom):
            tilemap.pset(rect.left, y, self._get_tile(FrameSlice.LEFT_TILE))
            tilemap.pset(rect.right, y, self._get_tile(FrameSlice.RIGHT_TILE))

    def _get_tile(self, frame_slice: FrameSlice) -> Tuple[int, int]:
        return self.slice_tiles.get(frame_slice, (0, 0))


def generate_frame_tilesets(input_data: Any, tile_packer: TilePacker) -> Dict[
        str, NineSlicingFrame]:
    """Generate frame tilesets that can be used to draw nine slicing frame on screen during screen
    processing.

    :param input_data: input data from JSON file (root -> frame_tilesets)
    :param tile_packer: tile packer used to pack tiles from frame tilesets
    :return: collection of generated frame tilesets
    """
    tilesets: Dict[str, NineSlicingFrame] = {}

    for tileset_name, tileset_data in input_data.items():
        tilesets[tileset_name] = NineSlicingFrame(
            {frame_slice: _pack_tile(tileset_data.get(frame_slice.value), tile_packer)
             for frame_slice in list(FrameSlice)})
        logging.info("Frame tileset '%s' added", tileset_name)

    logging.info("Total frame tilesets: %d", len(tilesets))

    return tilesets


def _pack_tile(tile_filename: str, tile_packer: TilePacker) -> Tuple[int, int]:
    return tile_packer.pack_tile(tile_filename) if tile_filename else (0, 0)
