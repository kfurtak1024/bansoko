# TODO: Rename this modele (core?!?!?!?!)
import abc
from enum import IntEnum, unique, Enum

from bansoko.game.tiles import Direction, TilePosition
from bansoko.graphics import Point, Rect
from bansoko.graphics.sprite import Sprite


# TODO: Rename it?
@unique
class LevelLayer(Enum):
    MAIN_LAYER = 0, Point(0, 0)
    LAYER_1 = 1, Point(-1, -1)
    LAYER_2 = 2, Point(-2, -2)

    def __init__(self, layer_index: int, offset: Point):
        self.layer_index = layer_index
        self.offset = offset

    @property
    def is_main(self) -> bool:
        return self == LevelLayer.MAIN_LAYER


class ObjectPosition:
    tile_position: TilePosition
    offset: Point

    def __init__(self, tile_position: TilePosition) -> None:
        self.tile_position = tile_position
        self.offset = Point(0, 0)

    def move(self, direction: Direction) -> None:
        self.tile_position = self.tile_position.move(direction)
        self.offset = Point(0, 0)

    def to_point(self) -> Point:
        return self.tile_position.to_point().offset(self.offset.x, self.offset.y)


class GameObject(abc.ABC):
    position: ObjectPosition

    def __init__(self, tile_position: TilePosition) -> None:
        self.position = ObjectPosition(tile_position)

    @property
    def tile_position(self) -> TilePosition:
        return self.position.tile_position

    def position_on_layer(self, layer: LevelLayer) -> Point:
        return self.position.to_point().offset(layer.offset.x, layer.offset.y)

    def draw(self, layer: LevelLayer) -> None:
        self._do_draw(self.position_on_layer(layer), layer)

    @abc.abstractmethod
    def _do_draw(self, position: Point, layer: LevelLayer) -> None:
        pass


@unique
class CrateState(IntEnum):
    MISPLACED = 0
    PLACED = 1


# TODO: Should become NamedTuple
class CrateSkin:
    def __init__(self) -> None:
        # TODO: Hard-coded sprites!
        self.crate_misplaced_sprite = Sprite(1, Rect.from_coords(0, 44, 10, 10), multilayer=True)
        self.crate_placed_sprite = Sprite(1, Rect.from_coords(0, 54, 10, 10), multilayer=True)

    def get_sprite(self, state: CrateState) -> Sprite:
        # TODO: Under construction!
        if state == CrateState.PLACED:
            return self.crate_placed_sprite
        return self.crate_misplaced_sprite


class Crate(GameObject):
    def __init__(self, tile_position: TilePosition, is_placed: bool, crate_skin: CrateSkin) -> None:
        super().__init__(tile_position)
        self.crate_skin = crate_skin
        self.state = CrateState.PLACED if is_placed else CrateState.MISPLACED

    @property
    def in_place(self) -> bool:
        return self.state == CrateState.PLACED

    def _do_draw(self, position: Point, layer: LevelLayer) -> None:
        sprite = self.crate_skin.get_sprite(self.state)
        sprite.draw(position, layer.layer_index)


@unique
class RobotState(IntEnum):
    STANDING = 0
    MOVING = 1
    PUSHING = 2


# TODO: Should become NamedTuple
class RobotSkin:
    def __init__(self) -> None:
        # TODO: Hard-coded sprites!
        self.robot_moving_sprite = Sprite(1, Rect.from_coords(0, 64, 10, 10), multilayer=True)
        self.robot_pushing_sprite = Sprite(1, Rect.from_coords(0, 74, 10, 10), multilayer=True)

    def get_sprite(self, state: RobotState, direction: Direction) -> Sprite:
        # TODO: Under construction!
        if state == RobotState.PUSHING:
            return self.robot_pushing_sprite

        return self.robot_moving_sprite


# TODO: Add animations
class Robot(GameObject):
    def __init__(self, tile_position: TilePosition, face_direction: Direction,
                 robot_skin: RobotSkin):
        super().__init__(tile_position)
        self.face_direction = face_direction
        self.robot_skin = robot_skin
        self.state = RobotState.STANDING

    def _do_draw(self, position: Point, layer: LevelLayer) -> None:
        sprite = self.robot_skin.get_sprite(self.state, self.face_direction)
        sprite.draw(position, layer.layer_index)
