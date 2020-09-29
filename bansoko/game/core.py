# TODO: Rename this modele (core?!?!?!?!)
import abc
from enum import IntEnum, unique

from bansoko.graphics import Point, Direction, Layer
from bansoko.graphics.sprite import SkinPack
from bansoko.graphics.tilemap import TilePosition


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

    @abc.abstractmethod
    def draw(self, layer: Layer) -> None:
        pass


@unique
class CrateState(IntEnum):
    MISPLACED = 0
    PLACED = 1


class Crate(GameObject):
    def __init__(self, tile_position: TilePosition, is_placed: bool, crate_skin: SkinPack) -> None:
        super().__init__(tile_position)
        self.crate_skin = crate_skin
        self.state = CrateState.PLACED if is_placed else CrateState.MISPLACED

    @property
    def in_place(self) -> bool:
        return self.state == CrateState.PLACED

    def draw(self, layer: Layer) -> None:
        sprite = self.crate_skin.skin_sprites[self.state]
        sprite.draw(self.position.to_point(), layer)


@unique
class RobotState(IntEnum):
    STANDING = 0
    MOVING = 1
    PUSHING = 2


# TODO: Add animations
class Robot(GameObject):
    def __init__(self, tile_position: TilePosition, face_direction: Direction,
                 robot_skin: SkinPack):
        super().__init__(tile_position)
        self.face_direction = face_direction
        self.robot_skin = robot_skin
        self.state = RobotState.STANDING

    def draw(self, layer: Layer) -> None:
        sprite = self.robot_skin.skin_sprites[self.state]
        sprite.draw(self.position.to_point(), layer, self.face_direction)
