from typing import NamedTuple, Tuple

from bansoko.game.core import Crate, Robot
from bansoko.game.tiles import Tileset, TileType
from bansoko.graphics import Layer, Point, Rect, Direction
from bansoko.graphics.sprite import SkinPack
from bansoko.graphics.tilemap import Tilemap, TILE_SIZE, TilePosition

# TODO: Should be taken from bundle

LEVEL_WIDTH = 32
LEVEL_HEIGHT = 32


class LevelTemplate(NamedTuple):
    level_num: int
    tilemap: Tilemap
    tileset: Tileset
    layers: Tuple[Layer, ...]
    robot_skin: SkinPack
    crate_skin: SkinPack

    @classmethod
    def from_level_num(cls, level_num: int, tileset_index: int, draw_offset: Point,
                       robot_skin: SkinPack, crate_skin: SkinPack) -> "LevelTemplate":
        tilemap_u = LEVEL_WIDTH * (level_num % TILE_SIZE)
        tilemap_v = LEVEL_HEIGHT * (level_num // TILE_SIZE)
        tilemap_uv_rect = Rect.from_coords(tilemap_u, tilemap_v, LEVEL_WIDTH, LEVEL_HEIGHT)
        tilemap = Tilemap(0, tilemap_uv_rect, 3)  # TODO: Hard-coded 3!
        tileset = Tileset(tileset_index)
        layers = tuple([Layer(i, draw_offset) for i in range(3)])  # TODO: Hard-coded 3!
        return cls(level_num=level_num, tilemap=tilemap, tileset=tileset, layers=layers,
                   robot_skin=robot_skin, crate_skin=crate_skin)

    def tile_at(self, position: TilePosition) -> TileType:
        return self.tileset.tile_of(self.tilemap.tile_index_at(position))

    def create_crates(self) -> Tuple[Crate, ...]:
        crates_positions = []
        for tile_position in self.tilemap.tiles_positions():
            if self.tile_at(tile_position).is_crate_spawn_point:
                crates_positions.append(tile_position)

        crates = []
        for crate_position in crates_positions:
            is_initially_placed = self.tile_at(crate_position).is_crate_initially_placed
            crates.append(Crate(crate_position, is_initially_placed, self.crate_skin))
        if not crates:
            raise Exception(f"Level {self.level_num} does not have any crates")

        return tuple(crates)

    def create_robot(self, face_direction: Direction) -> Robot:
        start = None
        for tile_position in self.tilemap.tiles_positions():
            if self.tile_at(tile_position).is_start:
                start = tile_position
        if not start:
            raise Exception(f"Level {self.level_num} does not have player start tile")

        return Robot(start, face_direction, self.robot_skin)
