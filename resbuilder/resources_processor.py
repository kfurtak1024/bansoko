from collections import namedtuple
from pathlib import Path

import pyxel

LEVEL_SIZE = 32
IMAGE_BANK_SIZE = 256
LEVEL_THUMBNAIL_SIZE = 32


def generate_tileset(level_tile_set, base_dir: str):
    image_bank = level_tile_set["image_bank"]
    pyxel.image(image_bank).load(0, 0, Path(base_dir).joinpath(level_tile_set["tile_void"]))
    pyxel.image(image_bank).load(8, 0, Path(base_dir).joinpath(level_tile_set["tile_wall"]))
    pyxel.image(image_bank).load(16, 0, Path(base_dir).joinpath(level_tile_set["tile_player_start"]))
    pyxel.image(image_bank).load(24, 0, Path(base_dir).joinpath(level_tile_set["tile_floor"]))
    pyxel.image(image_bank).load(32, 0, Path(base_dir).joinpath(level_tile_set["tile_crate"]))
    pyxel.image(image_bank).load(40, 0, Path(base_dir).joinpath(level_tile_set["tile_crate_placed"]))
    pyxel.image(image_bank).load(48, 0, Path(base_dir).joinpath(level_tile_set["tile_cargo_bay"]))


def generate_levels(levels, level_legend, level_thumbnail):
    image_bank = level_thumbnail["image_bank"]
    image = pyxel.image(image_bank)
    tile_map = pyxel.tilemap(0)
    symbols_to_colors = {
        level_legend["cell_void"]: level_thumbnail["color_void"],
        level_legend["cell_wall"]: level_thumbnail["color_wall"],
        level_legend["cell_player_start"]: level_thumbnail["color_player_start"],
        level_legend["cell_crate"]: level_thumbnail["color_crate"],
        level_legend["cell_crate_placed"]: level_thumbnail["color_crate_placed"],
        level_legend["cell_cargo_bay"]: level_thumbnail["color_cargo_bay"]
    }
    symbols_to_tiles = {
        level_legend["cell_void"]: 0,
        level_legend["cell_wall"]: 1,
        level_legend["cell_player_start"]: 2,
        level_legend["cell_crate"]: 4,
        level_legend["cell_crate_placed"]: 5,
        level_legend["cell_cargo_bay"]: 6
    }
    level_num = 0

    for level in levels:
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
                if symbol in symbols_to_tiles:
                    tile_map.set(x, y, symbols_to_tiles[symbol])
                if symbol == level_legend["cell_player_start"]:
                    start_x = x
                    start_y = y
                x = x + 1
            y = y + 1

        __flood_fill(start_x, start_y, tile_map, image)

        level_num = level_num + 1


def __level_thumbnail_x(level_num: int, level_width: int):
    return (level_num * LEVEL_THUMBNAIL_SIZE) % IMAGE_BANK_SIZE \
           + (LEVEL_THUMBNAIL_SIZE - level_width) / 2


def __level_thumbnail_y(level_num: int, level_height: int):
    return (level_num // (IMAGE_BANK_SIZE / LEVEL_THUMBNAIL_SIZE)) \
           * LEVEL_THUMBNAIL_SIZE + (LEVEL_THUMBNAIL_SIZE - level_height) / 2


Position = namedtuple("Position", ["x", "y"])


def __flood_fill(start_x: int, start_y: int, tile_map: pyxel.Tilemap, thumbnails_image: pyxel.Image) -> None:
    stack = list()
    stack.append(Position(int(start_x), int(start_y)))

    visited_map = [[False for i in range(LEVEL_SIZE)] for j in range(LEVEL_SIZE)]

    while len(stack) > 0:
        pos = stack.pop()
        local_pos = Position(pos.x % LEVEL_SIZE, pos.y % LEVEL_SIZE)
        pos_in_level_range = (local_pos.x >= 0) and (local_pos.x < LEVEL_SIZE) and (local_pos.y >= 0) and (local_pos.y < LEVEL_SIZE)
        wall_at_pos = tile_map.get(pos.x, pos.y) == 1  # TODO: Hard-coded WALL value
        not_visited_yet = not visited_map[local_pos.x][local_pos.y]

        if not wall_at_pos and pos_in_level_range and not_visited_yet:
            if tile_map.get(pos.x, pos.y) == 0:  # TODO: Hard-coded VOID value
                tile_map.set(pos.x, pos.y, 3)  # TODO: Hard-coded FLOOR value
                thumbnails_image.set(pos.x, pos.y, 7)  # TODO: Hard-coded FLOOR color
            stack.append(Position(pos.x - 1, pos.y))
            stack.append(Position(pos.x + 1, pos.y))
            stack.append(Position(pos.x, pos.y - 1))
            stack.append(Position(pos.x, pos.y + 1))
        visited_map[pos.x % LEVEL_SIZE][pos.y % LEVEL_SIZE] = True