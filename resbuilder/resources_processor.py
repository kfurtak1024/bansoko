from collections import namedtuple
from typing import List

import pyxel

from level_theme import LevelTheme
from tiles import IMAGE_BANK_SIZE, Tile

LEVEL_SIZE = 32
LEVEL_THUMBNAIL_SIZE = 32


def process_levels(levels, level_legend, level_themes: List[LevelTheme]):
    image_bank = 2  # TODO: Hard-coded image bank for thumbnails
    image = pyxel.image(image_bank)
    levels_metadata = []
    level_num = 0

    for level in levels:
        theme = level_themes[level_num % len(level_themes)]
        symbols_to_colors = {
            level_legend["cell_void"]: theme.thumbnail_color(Tile.VOID),
            level_legend["cell_wall"]: theme.thumbnail_color(Tile.WALL),
            level_legend["cell_player_start"]: theme.thumbnail_color(Tile.PLAYER_START),
            level_legend["cell_crate"]: theme.thumbnail_color(Tile.INITIAL_CRATE_POSITION),
            level_legend["cell_crate_placed"]: theme.thumbnail_color(Tile.CRATE_INITIALLY_PLACED),
            level_legend["cell_cargo_bay"]: theme.thumbnail_color(Tile.CARGO_BAY)
        }
        level_height = len(level["data"])
        y = __level_thumbnail_y(level_num, level_height)
        start_x = -1
        start_y = -1
        for data_row in level["data"]:
            level_width = len(data_row)
            x = __level_thumbnail_x(level_num, level_width)
            for symbol in data_row:
                if symbol in symbols_to_colors:
                    image.set(x, y, symbols_to_colors[symbol])

                for layer in range(0, theme.num_layers):
                    symbols_to_tiles = {
                        level_legend["cell_void"]: theme.tile_id(layer, Tile.VOID),
                        level_legend["cell_wall"]: theme.tile_id(layer, Tile.WALL),
                        level_legend["cell_player_start"]: theme.tile_id(layer, Tile.PLAYER_START),
                        level_legend["cell_crate"]: theme.tile_id(layer, Tile.INITIAL_CRATE_POSITION),
                        level_legend["cell_crate_placed"]: theme.tile_id(
                            layer, Tile.CRATE_INITIALLY_PLACED),
                        level_legend["cell_cargo_bay"]: theme.tile_id(layer, Tile.CARGO_BAY)
                    }
                    pyxel.tilemap(layer).set(x, y, symbols_to_tiles[symbol])

                if symbol == level_legend["cell_player_start"]:
                    start_x = x
                    start_y = y
                x = x + 1
            y = y + 1

        __flood_fill(start_x, start_y, 0, image, theme)

        levels_metadata.append({"tiles": __level_metadata(theme)})
        level_num = level_num + 1

    return levels_metadata


def __level_metadata(level_theme: LevelTheme):
    tiles_metadata = {}
    for tile in list(Tile):
        tiles_metadata[tile.theme_item_name] = [level_theme.tile_id(0, tile)]

    return tiles_metadata


def __level_thumbnail_x(level_num: int, level_width: int):
    return (level_num * LEVEL_THUMBNAIL_SIZE) % IMAGE_BANK_SIZE \
           + (LEVEL_THUMBNAIL_SIZE - level_width) / 2


def __level_thumbnail_y(level_num: int, level_height: int):
    return (level_num // (IMAGE_BANK_SIZE / LEVEL_THUMBNAIL_SIZE)) \
           * LEVEL_THUMBNAIL_SIZE + (LEVEL_THUMBNAIL_SIZE - level_height) / 2


Position = namedtuple("Position", ["x", "y"])


def __flood_fill(start_x: int, start_y: int, layer: int, thumbnails_image: pyxel.Image, level_theme: LevelTheme) -> None:
    stack = list()
    stack.append(Position(int(start_x), int(start_y)))

    visited_map = [[False for i in range(LEVEL_SIZE)] for j in range(LEVEL_SIZE)]

    while len(stack) > 0:
        pos = stack.pop()
        local_pos = Position(pos.x % LEVEL_SIZE, pos.y % LEVEL_SIZE)
        pos_in_level_range = (local_pos.x >= 0) and (local_pos.x < LEVEL_SIZE) and (local_pos.y >= 0) and (local_pos.y < LEVEL_SIZE)
        wall_at_pos = pyxel.tilemap(layer).get(pos.x, pos.y) == level_theme.tile_id(0, Tile.WALL)
        not_visited_yet = not visited_map[local_pos.x][local_pos.y]

        if not wall_at_pos and pos_in_level_range and not_visited_yet:
            if pyxel.tilemap(layer).get(pos.x, pos.y) == level_theme.tile_id(0, Tile.VOID):
                pyxel.tilemap(layer).set(pos.x, pos.y, level_theme.tile_id(0, Tile.FLOOR))
                thumbnails_image.set(pos.x, pos.y, level_theme.thumbnail_color(Tile.FLOOR))
            stack.append(Position(pos.x - 1, pos.y))
            stack.append(Position(pos.x + 1, pos.y))
            stack.append(Position(pos.x, pos.y - 1))
            stack.append(Position(pos.x, pos.y + 1))
        visited_map[pos.x % LEVEL_SIZE][pos.y % LEVEL_SIZE] = True
