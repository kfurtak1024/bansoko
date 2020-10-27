"""Module for processing levels."""
import itertools
import logging
import random
from dataclasses import dataclass
from typing import List, Dict, Any

import pyxel

from bansoko import LEVEL_THUMBNAIL_IMAGE_BANK, LEVEL_WIDTH, LEVEL_HEIGHT, TILEMAP_WIDTH
from bansoko.graphics import Point, Rect
from resbuilder.resources.level_themes import LevelTheme
from resbuilder.resources.tilemap_generators import TilemapGenerator
from resbuilder.resources.tiles import Tile, SYMBOL_TO_TILE


@dataclass
class _PreprocessedLevel:
    level_num: int
    width: int
    height: int
    tile_data: List[Tile]

    @property
    def start(self) -> Point:
        return self.offset_to_pos(self.tile_data.index(Tile.START))

    @property
    def tilemap_uv(self) -> Point:
        # TODO: This should take playfield area into account
        levels_horizontally = TILEMAP_WIDTH // LEVEL_WIDTH
        u = (self.level_num % levels_horizontally) * LEVEL_WIDTH \
            + (LEVEL_WIDTH - self.width) // 2
        v = (self.level_num // levels_horizontally) * LEVEL_HEIGHT \
            + (LEVEL_HEIGHT - self.height) // 2
        return Point(u, v)

    def get_tile_at(self, pos: Point) -> Tile:
        return self.tile_data[self.pos_to_offset(pos)]

    def set_tile_at(self, pos: Point, tile: Tile) -> None:
        self.tile_data[self.pos_to_offset(pos)] = tile

    def offset_to_pos(self, offset: int) -> Point:
        return Point(offset % self.width, offset // self.width)

    def pos_to_offset(self, pos: Point) -> int:
        return pos.y * self.width + pos.x

    def is_valid_offset(self, offset: int) -> bool:
        return 0 <= offset < (self.width * self.height)

    def is_valid_pos(self, pos: Point) -> bool:
        return self.is_valid_offset(self.pos_to_offset(pos))

    def flood_fill(self, start: Point, fill_tile: Tile, impassable_tile: Tile = Tile.WALL,
                   fillable_tile: Tile = Tile.VOID) -> None:
        """Flood fill level with given fill_tile, starting from position start and respecting
        impassable tiles.

        :param start: position where filling should start from
        :param fill_tile: tile to fill with
        :param impassable_tile: tile that represents barrier for flood fill
        :param fillable_tile: tile that can be replaced during filling
        """
        visited_map = [False] * (self.width * self.height)
        stack = list()
        stack.append(start)

        while len(stack) > 0:
            pos = stack.pop()
            if not self.is_valid_pos(pos):
                continue

            passable_tile = not self.get_tile_at(pos) == impassable_tile
            not_visited_yet = not visited_map[self.pos_to_offset(pos)]

            if passable_tile and not_visited_yet:
                if self.get_tile_at(pos) == fillable_tile:
                    self.set_tile_at(pos, fill_tile)
                stack.append(Point(pos.x - 1, pos.y))
                stack.append(Point(pos.x + 1, pos.y))
                stack.append(Point(pos.x, pos.y - 1))
                stack.append(Point(pos.x, pos.y + 1))
            visited_map[self.pos_to_offset(pos)] = True


def _preprocess_level(level_num: int, level_data: Any) -> _PreprocessedLevel:
    # TODO: Add some validation at this point
    flatten_data = [[SYMBOL_TO_TILE[symbol] for symbol in row_data] for row_data in level_data]
    level_width = len(flatten_data[0])
    level_height = len(flatten_data)
    tile_data = list(itertools.chain.from_iterable(flatten_data))

    preprocessed_level = _PreprocessedLevel(level_num, level_width, level_height, tile_data)
    preprocessed_level.flood_fill(preprocessed_level.start, Tile.FLOOR)

    return preprocessed_level


def _generate_background(level_num: int, seed: int, tile_generator: TilemapGenerator) -> None:
    # TODO: Refactor this!
    random.seed(seed)
    levels_horizontally = TILEMAP_WIDTH // LEVEL_WIDTH
    tilemap_rect = Rect.from_coords(
        (level_num % levels_horizontally) * LEVEL_WIDTH,
        (level_num // levels_horizontally) * LEVEL_HEIGHT,
        LEVEL_WIDTH, LEVEL_HEIGHT)

    tilemap_points = tilemap_rect.inside_points()

    for point in tilemap_points:
        tile = tile_generator.next_tile()
        if tile:
            pyxel.tilemap(0).set(point.x, point.y, tile)


def _generate_tilemap_and_thumbnail(preprocessed_level: _PreprocessedLevel,
                                    level_theme: LevelTheme) -> None:
    thumbnails_image = pyxel.image(LEVEL_THUMBNAIL_IMAGE_BANK)
    tilemap_uv = preprocessed_level.tilemap_uv
    for offset, tile in enumerate(preprocessed_level.tile_data):
        local_pos = preprocessed_level.offset_to_pos(offset)
        tilemap_pos = Point(tilemap_uv.x + local_pos.x, tilemap_uv.y + local_pos.y)
        thumbnails_image.set(tilemap_pos.x, tilemap_pos.y, level_theme.thumbnail_color(tile))

        if tile is not Tile.VOID:
            for layer in range(0, level_theme.num_layers):
                pyxel.tilemap(layer).set(tilemap_pos.x, tilemap_pos.y,
                                         level_theme.tile_id(layer, tile))


def process_levels(input_data: Any, level_themes: List[LevelTheme],
                   tilemap_generators: Dict[str, TilemapGenerator]) -> Any:
    """Process and produce level metadata from input resource file.

    Levels are first pre-processed from human-readable format (format of input resource file) and
    then stored in Pyxel's tilemaps along with resources metadata file.
    Level theme is assigned basing on a level number.
    Floor tiles are automatically generated basing on player starting position and walls positions.

    :param input_data: input data from JSON file (root -> levels)
    :param level_themes: collection of processed level themes that level can use
    :param tilemap_generators: collection of processed tilemap generators that level can use
    :return: levels metadata (ready to be serialized to JSON)
    """
    levels_metadata = []

    for level_num, level_data in enumerate(input_data):
        level_theme_id = level_num % len(level_themes)
        level_theme = level_themes[level_theme_id]
        tile_generator = tilemap_generators[level_theme.background_generator]
        preprocessed_level = _preprocess_level(level_num, level_data["data"])
        _generate_background(level_num, level_data.get("seed", level_num), tile_generator)
        _generate_tilemap_and_thumbnail(preprocessed_level, level_theme)

        levels_metadata.append({
            "tileset": level_theme_id,
            "draw_offset": [0, 0],  # TODO: Hard-coded for now!
            "robot_sprite_pack": level_theme.robot_sprite_pack,
            "crate_sprite_pack": level_theme.crate_sprite_pack
        })
        logging.info("Level %d (%dx%d tileset:%d) added", level_num, preprocessed_level.width,
                     preprocessed_level.height, level_theme_id)

    logging.info("Total levels: %d", len(levels_metadata))
    return levels_metadata
