"""Module exposing level template."""
from dataclasses import dataclass
from typing import Tuple, Dict

from bansoko import GAME_FRAME_TIME_IN_MS, LEVEL_WIDTH, LEVEL_HEIGHT, LEVEL_NUM_LAYERS, \
    LEVEL_BASE_TILEMAP
from bansoko.game import GameError
from bansoko.game.game_object import Crate, Robot, RobotState, CrateState
from bansoko.game.tiles import Tileset, TileType
from bansoko.graphics import Layer, Point, Rect, Direction, TILE_SIZE
from bansoko.graphics.animation import Animation
from bansoko.graphics.sprite import SpritePack, Sprite
from bansoko.graphics.tilemap import Tilemap, TilePosition


@dataclass(frozen=True)
class LevelSpritePacks:
    """
    Collection of sprite packs used by a level.

    Attributes:
        robot_sprite_pack - sprite pack containing all robot related sprites
        crate_sprite_pack - sprite pack containing all crate related sprites
    """
    robot_sprite_pack: SpritePack
    crate_sprite_pack: SpritePack

    @property
    def robot_animations(self) -> Dict[RobotState, Animation]:
        """The pack of animations for all robot states."""
        return {
            RobotState.STANDING: Animation(
                sprite=self.robot_sprite_pack.sprites[RobotState.STANDING],
                frame_length=GAME_FRAME_TIME_IN_MS),
            RobotState.MOVING: Animation(
                sprite=self.robot_sprite_pack.sprites[RobotState.MOVING],
                frame_length=GAME_FRAME_TIME_IN_MS,
                looped=True),
            RobotState.PUSHING: Animation(
                sprite=self.robot_sprite_pack.sprites[RobotState.PUSHING],
                frame_length=GAME_FRAME_TIME_IN_MS,
                looped=True)
        }

    @property
    def crate_sprites(self) -> Dict[CrateState, Sprite]:
        """The pack of sprites for all crate states."""
        return {
            CrateState.MISPLACED: self.crate_sprite_pack.sprites[0],
            CrateState.PLACED: self.crate_sprite_pack.sprites[1]
        }


@dataclass(frozen=True)
class LevelTemplate:
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
        """Create a new level template for given level number.

        :param level_num: level number to create level template for
        :param tileset_index: index of first tile (starting tile) used in the template
        :param draw_offset: the initial offset of the level (u3sed when level is drawn)
        :param sprite_packs: sprite packs used in the level
        :return: newly created level template
        """
        tilemap_u = LEVEL_WIDTH * (level_num % TILE_SIZE)
        tilemap_v = LEVEL_HEIGHT * (level_num // TILE_SIZE)
        tilemap_uv_rect = Rect.from_coords(tilemap_u, tilemap_v, LEVEL_WIDTH, LEVEL_HEIGHT)
        tilemap = Tilemap(LEVEL_BASE_TILEMAP, tilemap_uv_rect, LEVEL_NUM_LAYERS)
        tileset = Tileset(tileset_index)
        layers = tuple(
            [Layer(i, opaque=(i == 0), global_offset=draw_offset) for i in range(LEVEL_NUM_LAYERS)])
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
                Crate(crate_position, is_initially_placed, self.sprite_packs.crate_sprites))
        if not crates:
            raise GameError(f"Level {self.level_num} does not have any crates")

        return tuple(crates)

    def create_robot(self) -> Robot:
        """Create robot instance based on information from tilemap about its start position."""
        start = None
        for tile_position in self.tilemap.tiles_positions():
            if self.tile_at(tile_position).is_start:
                start = tile_position
        if not start:
            raise GameError(f"Level {self.level_num} does not have player start tile")

        face_direction = Direction.UP
        for direction in list(Direction):
            if self.tile_at(start.move(direction)).is_walkable:
                face_direction = direction
                break

        return Robot(start, face_direction, self.sprite_packs.robot_animations)
