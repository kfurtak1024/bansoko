import itertools
import logging
import random
from collections import namedtuple
from typing import List, Dict, Optional

import pyxel

from resbuilder.processors.level_themes import LevelTheme
from resbuilder.processors.tilemap_generators import TilemapGenerator
from resbuilder.processors.tiles import IMAGE_BANK_SIZE, Tile, SYMBOL_TO_TILE


LEVEL_WIDTH = 32
LEVEL_HEIGHT = 32


# TODO: Add error handling!
def process_levels(levels, level_themes: List[LevelTheme],
                   tilemap_generators: Dict[str, TilemapGenerator]):
    thumbnails_image = pyxel.image(2)  # TODO: Hard-coded image bank for thumbnails
    levels_metadata = []

    for level_num, level in enumerate(levels):
        theme_id = level_num % len(level_themes)
        theme = level_themes[theme_id]
        tile_generator = tilemap_generators[theme.background_generator]
        preprocessed_level = _preprocess_level(level_num, level["data"])
        tilemap_uv = preprocessed_level.tilemap_uv

        _generate_background(level_num, level.get("seed", level_num), tile_generator)

        for offset, tile in enumerate(preprocessed_level.tile_data):
            local_pos = preprocessed_level.offset_to_pos(offset)
            tilemap_pos = Position(tilemap_uv.x + local_pos.x, tilemap_uv.y + local_pos.y)
            thumbnails_image.set(tilemap_pos.x, tilemap_pos.y, theme.thumbnail_color(tile))

            if tile is not Tile.VOID:
                for layer in range(0, theme.num_layers):
                    pyxel.tilemap(layer).set(tilemap_pos.x, tilemap_pos.y, theme.tile_id(layer, tile))

        levels_metadata.append({
            "tileset": theme_id,
            "draw_offset": [0, 0],
            "robot_skin": theme.robot_skin,
            "crate_skin": theme.crate_skin
        })
        logging.info("Level %d (%dx%d tileset:%d) added", level_num, preprocessed_level.width,
                     preprocessed_level.height, theme_id)

    logging.info("Total levels: %d", len(levels))
    return levels_metadata


def _generate_background(level_num: int, seed: int, tile_generator: TilemapGenerator) -> None:
    # TODO: Refactor this!
    random.seed(seed)
    levels_horizontally = IMAGE_BANK_SIZE // LEVEL_WIDTH
    offset = Position(
        (level_num % levels_horizontally) * LEVEL_WIDTH,
        (level_num // levels_horizontally) * LEVEL_HEIGHT)
    for y in range(LEVEL_WIDTH):
        for x in range(LEVEL_HEIGHT):
            tile = tile_generator.next_tile()
            if tile:
                pyxel.tilemap(0).set(offset.x + x, offset.y + y, tile)


Position = namedtuple("Position", ["x", "y"])


class PreprocessedLevel:
    def __init__(self, level_num: int, width: int, height: int, tile_data: List[Tile]) -> None:
        self.level_num = level_num
        self.tile_data = tile_data
        self.width = width
        self.height = height
        self.start = self.offset_to_pos(self.tile_data.index(Tile.START))

    @property
    def tilemap_uv(self) -> Position:
        # TODO: This should take playfield area into account
        levels_horizontally = IMAGE_BANK_SIZE // LEVEL_WIDTH
        u = (self.level_num % levels_horizontally) * LEVEL_WIDTH \
            + (LEVEL_WIDTH - self.width) // 2
        v = (self.level_num // levels_horizontally) * LEVEL_HEIGHT \
            + (LEVEL_HEIGHT - self.height) // 2
        return Position(u, v)

    def get_tile_at(self, pos: Position) -> Tile:
        return self.tile_data[self.pos_to_offset(pos)]

    def set_tile_at(self, pos: Position, tile: Tile) -> None:
        self.tile_data[self.pos_to_offset(pos)] = tile

    def offset_to_pos(self, offset: int) -> Position:
        return Position(offset % self.width, offset // self.width)

    def pos_to_offset(self, pos: Position) -> int:
        return pos.y * self.width + pos.x

    def valid_offset(self, offset: int) -> bool:
        return 0 <= offset < (self.width * self.height)

    def valid_pos(self, pos: Position) -> bool:
        return self.valid_offset(self.pos_to_offset(pos))

    def flood_fill(self, start: Position, fill_tile: Tile, impassable_tile: Tile = Tile.WALL,
                   fillable_tile: Tile = Tile.VOID) -> None:
        visited_map = [False] * (self.width * self.height)
        stack = list()
        stack.append(start)

        while len(stack) > 0:
            pos = stack.pop()
            if not self.valid_pos(pos):
                continue

            passable_tile = not self.get_tile_at(pos) == impassable_tile
            not_visited_yet = not visited_map[self.pos_to_offset(pos)]

            if passable_tile and not_visited_yet:
                if self.get_tile_at(pos) == fillable_tile:
                    self.set_tile_at(pos, fill_tile)
                stack.append(Position(pos.x - 1, pos.y))
                stack.append(Position(pos.x + 1, pos.y))
                stack.append(Position(pos.x, pos.y - 1))
                stack.append(Position(pos.x, pos.y + 1))
            visited_map[self.pos_to_offset(pos)] = True


def _preprocess_level(level_num: int, level_data) -> PreprocessedLevel:
    # TODO: Add some validation at this point
    flatten_data = [[SYMBOL_TO_TILE[symbol] for symbol in row_data] for row_data in level_data]
    level_width = len(flatten_data[0])
    level_height = len(flatten_data)
    tile_data = list(itertools.chain.from_iterable(flatten_data))

    preprocessed_level = PreprocessedLevel(level_num, level_width, level_height, tile_data)
    preprocessed_level.flood_fill(preprocessed_level.start, Tile.FLOOR)

    return preprocessed_level
