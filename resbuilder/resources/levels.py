"""Module for processing levels."""
import hashlib
import logging
from collections import Counter
from itertools import chain
from typing import List, Dict, Any, Generator, Tuple

import pyxel

from bansoko import LEVEL_THUMBNAIL_IMAGE_BANK, LEVEL_WIDTH, LEVEL_HEIGHT, LEVEL_BASE_TILEMAP
from bansoko.graphics import Point, Direction, Size, TILE_SIZE
from resbuilder import ResourceError
from resbuilder.resources.backgrounds import TilemapGenerator
from resbuilder.resources.level_themes import LevelTheme
from resbuilder.resources.tiles import Tile, SYMBOL_TO_TILE, tilemap_rect_nth


class _PreprocessedLevel:
    def __init__(self, level_num: int, raw_data: List[List[Tile]]) -> None:
        self.level_num = level_num
        self.tilemap_data = [Tile.VOID] * (LEVEL_WIDTH * LEVEL_HEIGHT)
        self.size = Size(len(raw_data[0]), len(raw_data))

        offset = Point((LEVEL_WIDTH - self.size.width) // 2,
                       (LEVEL_HEIGHT - self.size.height) // 2)

        for y in range(self.size.height):
            for x in range(self.size.width):
                pos = Point(x, y).offset(offset)
                self.tilemap_data[self._pos_to_offset(pos)] = raw_data[y][x]

    @property
    def start(self) -> Point:
        """Player's start position in level."""
        return self._offset_to_pos(self.tilemap_data.index(Tile.START))

    @property
    def tilemap_offset(self) -> Point:
        """Offset of the tilemap, for properly centering on the screen."""
        return Point(
            (self.size.width % 2) * TILE_SIZE // 2,
            (self.size.height % 2) * TILE_SIZE // 2)

    def tile_positions(self) -> Generator[Tuple[Point, Point], None, None]:
        """Generator for iterating over all valid tile positions inside both level and Pyxel's
        mega-tilemap (from top-left to bottom-right)."""
        tilemap_rect = tilemap_rect_nth(self.level_num)
        tilemap_points = tilemap_rect.inside_points()

        for point in tilemap_points:
            yield point.offset(Point(-tilemap_rect.x, -tilemap_rect.y)), point

    def get_tile_at(self, pos: Point) -> Tile:
        """Return tile at given position.

        :param pos: position to get tile at
        :return: tile at given position
        """
        return self.tilemap_data[self._pos_to_offset(pos)]

    def set_tile_at(self, pos: Point, tile: Tile) -> None:
        """Put tile at given position.

        :param pos: position to put tile at
        :param tile: tile to be put
        """
        self.tilemap_data[self._pos_to_offset(pos)] = tile

    def flood_fill(self, start: Point, fill_tile: Tile, impassable_tile: Tile = Tile.WALL,
                   fillable_tile: Tile = Tile.VOID) -> None:
        """Flood fill level with given fill_tile, starting from position start and respecting
        impassable tiles.

        :param start: position where filling should start from
        :param fill_tile: tile to fill with
        :param impassable_tile: tile that represents barrier for flood fill
        :param fillable_tile: tile that can be replaced during filling
        """
        visited_map = [False] * (LEVEL_WIDTH * LEVEL_HEIGHT)
        stack = list()
        stack.append(start)

        while len(stack) > 0:
            pos = stack.pop()
            if not self._is_valid_pos(pos):
                continue

            passable_tile = not self.get_tile_at(pos) == impassable_tile
            not_visited_yet = not visited_map[self._pos_to_offset(pos)]

            if passable_tile and not_visited_yet:
                if self.get_tile_at(pos) == fillable_tile:
                    self.set_tile_at(pos, fill_tile)
                stack.append(pos.move(Direction.LEFT))
                stack.append(pos.move(Direction.RIGHT))
                stack.append(pos.move(Direction.UP))
                stack.append(pos.move(Direction.DOWN))
            visited_map[self._pos_to_offset(pos)] = True

    @staticmethod
    def _offset_to_pos(offset: int) -> Point:
        return Point(offset % LEVEL_WIDTH, offset // LEVEL_WIDTH)

    @staticmethod
    def _pos_to_offset(pos: Point) -> int:
        return pos.y * LEVEL_WIDTH + pos.x

    @staticmethod
    def _is_valid_offset(offset: int) -> bool:
        return 0 <= offset < (LEVEL_WIDTH * LEVEL_HEIGHT)

    def _is_valid_pos(self, pos: Point) -> bool:
        return self._is_valid_offset(self._pos_to_offset(pos))


def _preprocess_level(level_num: int, level_data: Any) -> _PreprocessedLevel:
    raw_data = [[SYMBOL_TO_TILE[symbol] for symbol in row_data] for row_data in level_data]
    _validate_level(raw_data)
    preprocessed_level = _PreprocessedLevel(level_num, raw_data)
    preprocessed_level.flood_fill(preprocessed_level.start, Tile.FLOOR)
    return preprocessed_level


def _validate_level(level_data: List[List[Tile]]) -> None:
    level_size = Size(len(level_data[0]), len(level_data))
    if level_size.width > LEVEL_WIDTH:
        raise ResourceError(f"Level exceeds maximum level width ({LEVEL_WIDTH})")
    if level_size.height > LEVEL_HEIGHT:
        raise ResourceError(f"Level exceeds maximum level height ({LEVEL_WIDTH})")

    tile_counter = Counter(list(chain.from_iterable(level_data)))
    if tile_counter.get(Tile.START, 0) == 0:
        raise ResourceError("Level is missing player start position")
    if tile_counter.get(Tile.START, 0) > 1:
        raise ResourceError("Level has more than one player start position")

    num_of_crates = tile_counter.get(Tile.CRATE_INITIALLY_PLACED, 0) + tile_counter.get(
        Tile.INITIAL_CRATE_POSITION, 0)
    num_of_not_initially_placed_crates = tile_counter.get(
        Tile.INITIAL_CRATE_POSITION, 0)
    num_of_cargo_bays = tile_counter.get(Tile.CRATE_INITIALLY_PLACED, 0) + tile_counter.get(
        Tile.CARGO_BAY, 0)

    if num_of_crates == 0:
        raise ResourceError("Level has no crates")
    if num_of_cargo_bays == 0:
        raise ResourceError("Level has no cargo bays")
    if num_of_crates > num_of_cargo_bays:
        raise ResourceError("Level has more crates than cargo bays")
    if num_of_crates < num_of_cargo_bays:
        raise ResourceError("Level has more cargo bays than crates")
    if num_of_not_initially_placed_crates == 0:
        raise ResourceError("Level must have at least one crate that is not initially placed in "
                            "cargo bay")


def _generate_background(level_num: int, seed: int, tile_generator: TilemapGenerator) -> None:
    tile_generator.generate_tilemap(LEVEL_BASE_TILEMAP, tilemap_rect_nth(level_num), seed)


def _generate_tilemap_and_thumbnail(preprocessed_level: _PreprocessedLevel,
                                    level_theme: LevelTheme) -> None:
    thumbnails_image = pyxel.image(LEVEL_THUMBNAIL_IMAGE_BANK)
    tile_positions = preprocessed_level.tile_positions()
    for level_pos, tilemap_pos in tile_positions:
        tile = preprocessed_level.get_tile_at(level_pos)
        thumbnails_image.set(tilemap_pos.x, tilemap_pos.y, level_theme.thumbnail_color(tile))

        if tile is not Tile.VOID:
            for layer in range(level_theme.num_layers):
                tile_id = level_theme.tile_id(layer, tile)
                pyxel.tilemap(layer).set(tilemap_pos.x, tilemap_pos.y, tile_id)


def _update_sha1(level_data: Any, sha1: Any) -> None:
    for row_data in level_data:
        sha1.update(row_data.encode())


def process_levels(input_data: Any, level_themes: List[LevelTheme],
                   tilemap_generators: Dict[str, TilemapGenerator], bundle_name: str) -> Any:
    """Process and produce level metadata from input resource file.

    Levels are first pre-processed from human-readable format (format of input resource file) and
    then stored in Pyxel's mega-tilemaps along with resources metadata file.
    Level theme is assigned basing on a level number.
    Floor tiles are automatically generated basing on player starting position and walls positions.

    :param input_data: input data from JSON file (root -> levels)
    :param level_themes: collection of processed level themes that level can use
    :param tilemap_generators: collection of processed tilemap generators that level can use
    :param bundle_name: the name of the bundle levels are processed for
    :return: levels metadata (ready to be serialized to JSON)
    """
    level_templates = []
    sha1 = hashlib.sha1()
    sha1.update(bundle_name.encode())

    for level_num, level_data in enumerate(input_data):
        level_theme_id = level_num % len(level_themes)
        level_theme = level_themes[level_theme_id]
        tile_generator = tilemap_generators[level_theme.background_generator]
        _update_sha1(level_data["data"], sha1)
        preprocessed_level = _preprocess_level(level_num, level_data["data"])
        _generate_background(level_num, level_data.get("seed", level_num), tile_generator)
        _generate_tilemap_and_thumbnail(preprocessed_level, level_theme)
        level_draw_offset = preprocessed_level.tilemap_offset.offset(level_theme.tilemap_offset)

        level_templates.append({
            "tileset": level_theme_id,
            "draw_offset": level_draw_offset.as_list,
            "robot_sprite_pack_ref": level_theme.robot_sprite_pack,
            "crate_sprite_pack_ref": level_theme.crate_sprite_pack
        })
        logging.info("Level %d (%dx%d tileset:%d) added", level_num, preprocessed_level.size.width,
                     preprocessed_level.size.height, level_theme_id)

    logging.info("Total levels: %d", len(level_templates))
    return {
        "sha1": sha1.hexdigest(),
        "level_templates": level_templates
    }
