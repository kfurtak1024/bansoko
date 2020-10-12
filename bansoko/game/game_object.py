"""Module exposing all game objects."""
import abc
from enum import IntEnum, unique
from typing import Optional, Dict

from bansoko.graphics import Point, Direction, Layer
from bansoko.graphics.animation import AnimationPlayer, Animation
from bansoko.graphics.sprite import Sprite
from bansoko.graphics.tilemap import TilePosition, TILE_SIZE


# TODO: Rename it
class MovementStats:
    """Statistics of player's movement.

    Attributes:
        pushes - number of moves that player made
        steps - number of steps that player made
    """
    pushes: int = 0
    steps: int = 0


class ObjectPosition:
    tile_position: TilePosition
    offset: Point

    def __init__(self, tile_position: TilePosition) -> None:
        self.tile_position = tile_position
        self.offset = Point(0, 0)

    def move(self, direction: Direction) -> None:
        """Move object position in given direction by one tile.

        Additionally reset offset.

        :param direction: direction of the movement
        """
        self.tile_position = self.tile_position.move(direction)
        self.offset = Point(0, 0)

    def to_point(self) -> Point:
        """Convert tile position to a point in screen space (taking into account the offset)."""
        return self.tile_position.to_point().offset(self.offset.x, self.offset.y)


class GameObject(abc.ABC):
    """This is an abstract, base class for all game objects.

    Attributes:
        position - game object position
    """
    position: ObjectPosition

    def __init__(self, tile_position: TilePosition) -> None:
        self.position = ObjectPosition(tile_position)

    @property
    def tile_position(self) -> TilePosition:
        """The position in tilemap this game object is located at."""
        return self.position.tile_position

    def update(self) -> None:
        """Update game object.

        Called once per frame.
        """

    @abc.abstractmethod
    def draw(self, layer: Layer) -> None:
        """Draw game object on given layer.

        Called once per frame.

        :param layer: layer the game object is drawn on
        """


@unique
class RobotState(IntEnum):
    """Enum defining all states robot can be in.

    When no action is performed robot is in STANDING state. From there it can either transition to
    PUSHING state (when there is a crate that can be moved in robot moving direction) or MOVING
    state otherwise.
    """
    STANDING = 0
    MOVING = 1
    PUSHING = 2


class Robot(GameObject):
    _robot_state: RobotState

    def __init__(self, tile_position: TilePosition, face_direction: Direction,
                 robot_animations: Dict[RobotState, Animation]):
        super().__init__(tile_position)
        self.face_direction = face_direction
        self.robot_animations = robot_animations
        self.animation_player = AnimationPlayer()
        self.robot_state = RobotState.STANDING

    @property
    def robot_state(self) -> RobotState:
        return self._robot_state

    @robot_state.setter
    def robot_state(self, robot_state: RobotState) -> None:
        self.animation_player.play(self.robot_animations[robot_state])
        self._robot_state = robot_state

    def update(self) -> None:
        self.animation_player.update()

    def draw(self, layer: Layer) -> None:
        self.animation_player.draw(self.position.to_point(), layer, self.face_direction)


@unique
class CrateState(IntEnum):
    """Enum defining all states crate can be in.

    Crates can be either PLACED (when they are located in cargo bays) or MISPLACED otherwise.
    """
    MISPLACED = 0
    PLACED = 1


class Crate(GameObject):
    def __init__(self, tile_position: TilePosition, is_placed: bool,
                 crate_sprites: Dict[CrateState, Sprite]) -> None:
        super().__init__(tile_position)
        self.crate_sprites = crate_sprites
        self.state = CrateState.PLACED if is_placed else CrateState.MISPLACED

    @property
    def in_place(self) -> bool:
        """Is the crate placed on a cargo bay tile."""
        return self.state == CrateState.PLACED

    def draw(self, layer: Layer) -> None:
        sprite = self.crate_sprites[self.state]
        sprite.draw(self.position.to_point(), layer)
