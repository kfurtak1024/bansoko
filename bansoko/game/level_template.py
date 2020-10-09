"""Module exposing level template."""
from typing import NamedTuple, Tuple

from bansoko.game.game_object import Crate, Robot
from bansoko.game.tiles import Tileset, TileType
from bansoko.graphics import Layer, Point, Rect, Direction
from bansoko.graphics.sprite import SpritePack
from bansoko.graphics.tilemap import Tilemap, TILE_SIZE, TilePosition

# TODO: Should be taken from bundle

LEVEL_WIDTH = 32
LEVEL_HEIGHT = 32


class LevelSpritePacks(NamedTuple):
    """
    Collection of sprite packs used by a level.

    Attributes:
        robot_sprite_pack - sprite pack containing all robot related sprites
        crate_sprite_pack - sprite pack containing all crate related sprites
    """
    robot_sprite_pack: SpritePack
    crate_sprite_pack: SpritePack


class LevelTemplate(NamedTuple):
    """LevelTemplate is a blue-print used for level creation.

    Attributes:
        level_num - the level number
        tilemap - tilemap to be used in the level
        tileset -  tileset to be used in the level
        layers - list of layers level will be drawn on
        sprite_packs - sprite packs to be used in the level
    """
    level_num: int
    tilemap: Tilemap
    tileset: Tileset
    layers: Tuple[Layer, ...]
    sprite_packs: LevelSpritePacks

    @classmethod
    def from_level_num(cls, level_num: int, tileset_index: int, draw_offset: Point,
                       sprite_packs: LevelSpritePacks) -> "LevelTemplate":
        tilemap_u = LEVEL_WIDTH * (level_num % TILE_SIZE)
        tilemap_v = LEVEL_HEIGHT * (level_num // TILE_SIZE)
        tilemap_uv_rect = Rect.from_coords(tilemap_u, tilemap_v, LEVEL_WIDTH, LEVEL_HEIGHT)
        tilemap = Tilemap(0, tilemap_uv_rect, 3)  # TODO: Hard-coded 3!
        tileset = Tileset(tileset_index)
        layers = tuple([Layer(i, draw_offset) for i in range(3)])  # TODO: Hard-coded 3!
        return cls(level_num=level_num, tilemap=tilemap, tileset=tileset, layers=layers,
                   sprite_packs=sprite_packs)

    def tile_at(self, position: TilePosition) -> TileType:
        """Return the type of tile at given position in tilemap.

        :param position: position of the tile to check tile type of
        :return: type of the tile at given position
        """
        return self.tileset.tile_of(self.tilemap.tile_index_at(position))

    def create_crates(self) -> Tuple[Crate, ...]:
        """Create a collection of crates based on information from tilemap about their initial
        positions.

        :return: collection of crates created from level template
        """
        crates_positions = []
        for tile_position in self.tilemap.tiles_positions():
            if self.tile_at(tile_position).is_crate_spawn_point:
                crates_positions.append(tile_position)

        crates = []
        for crate_position in crates_positions:
            is_initially_placed = self.tile_at(crate_position).is_crate_initially_placed
            crates.append(
                Crate(crate_position, is_initially_placed, self.sprite_packs.crate_sprite_pack))
        if not crates:
            raise Exception(f"Level {self.level_num} does not have any crates")

        return tuple(crates)

    def create_robot(self, face_direction: Direction) -> Robot:
        """Create robot instance based on information from tilemap about its start position.

        :param face_direction: direction the robot should be facing to
        :return: instance of robot created from level template
        """
        start = None
        for tile_position in self.tilemap.tiles_positions():
            if self.tile_at(tile_position).is_start:
                start = tile_position
        if not start:
            raise Exception(f"Level {self.level_num} does not have player start tile")

        return Robot(start, face_direction, self.sprite_packs.robot_sprite_pack)
