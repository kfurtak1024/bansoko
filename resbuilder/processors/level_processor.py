import itertools
from collections import namedtuple
from typing import List

import pyxel

from processors.level_theme_processor import LevelTheme
from processors.tile_processor import IMAGE_BANK_SIZE, Tile

LEVEL_SIZE = 32

# TODO: Add error handling!


def process_levels(levels, level_legend, level_themes: List[LevelTheme]):
    thumbnails_image = pyxel.image(2) # TODO: Hard-coded image bank for thumbnails
    levels_metadata = []

    for level_num, level in enumerate(levels):
        theme = level_themes[level_num % len(level_themes)]

        preprocessed_level = _preprocess_level(level_num, level["data"], level_legend)

        for offset, tile in enumerate(preprocessed_level.tile_data):
            local_pos = preprocessed_level.offset_to_pos(offset)
            tilemap_pos = Position(preprocessed_level.tilemap_uv.x + local_pos.x, preprocessed_level.tilemap_uv.y + local_pos.y)  # TODO: Waaaay to long line

            thumbnails_image.set(tilemap_pos.x, tilemap_pos.y, theme.thumbnail_color(tile))

            for layer in range(0, theme.num_layers):
                pyxel.tilemap(layer).set(tilemap_pos.x, tilemap_pos.y, theme.tile_id(layer, tile))

        levels_metadata.append({"tiles": __level_metadata(theme)})

    return levels_metadata


Position = namedtuple("Position", ["x", "y"])


class PreprocessedLevel:
    def __init__(self, level_num: int, width: int, height: int, tile_data: List[Tile]):
        self.level_num = level_num
        self.tile_data = tile_data
        self.width = width
        self.height = height
        # TODO: Find player start
        self.player_start = self.offset_to_pos(self.tile_data.index(Tile.PLAYER_START))

    # TODO: Return int!!
    @property
    def tilemap_uv(self) -> Position:
        u = (self.level_num * LEVEL_SIZE) % IMAGE_BANK_SIZE + (LEVEL_SIZE - self.width) / 2
        v = (self.level_num // (IMAGE_BANK_SIZE / LEVEL_SIZE)) * LEVEL_SIZE + (LEVEL_SIZE - self.height) / 2
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
        return (offset >= 0) and (offset < self.width * self.height)

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

            passable_tile = not (self.get_tile_at(pos) == impassable_tile)
            not_visited_yet = not visited_map[self.pos_to_offset(pos)]

            if passable_tile and not_visited_yet:
                if self.get_tile_at(pos) == fillable_tile:
                    self.set_tile_at(pos, fill_tile)
                stack.append(Position(pos.x - 1, pos.y))
                stack.append(Position(pos.x + 1, pos.y))
                stack.append(Position(pos.x, pos.y - 1))
                stack.append(Position(pos.x, pos.y + 1))
            visited_map[self.pos_to_offset(pos)] = True


def _preprocess_level(level_num: int, level_data, level_legend) -> PreprocessedLevel:
    # TODO: Refactor this!
    symbols_to_tiles = {
        level_legend["cell_void"]: Tile.VOID,
        level_legend["cell_wall"]: Tile.WALL,
        level_legend["cell_player_start"]: Tile.PLAYER_START,
        level_legend["cell_crate"]: Tile.INITIAL_CRATE_POSITION,
        level_legend["cell_crate_placed"]: Tile.CRATE_INITIALLY_PLACED,
        level_legend["cell_cargo_bay"]: Tile.CARGO_BAY
    }

    data = [[symbols_to_tiles[cell] for cell in row_data] for row_data in level_data]

    preprocessed_level = PreprocessedLevel(level_num, len(data[0]), len(data), list(itertools.chain.from_iterable(data)))
    preprocessed_level.flood_fill(preprocessed_level.player_start, Tile.FLOOR)

    return preprocessed_level


# TODO: Move it to level_theme_processor
def __level_metadata(level_theme: LevelTheme):
    tiles_metadata = {}
    for tile in list(Tile):
        tiles_metadata[tile.theme_item_name] = level_theme.tile_id(0, tile)

    return tiles_metadata
