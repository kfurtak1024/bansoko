"""Module exposing all game objects."""
import abc
from dataclasses import dataclass
from enum import IntEnum, unique
from typing import Dict

from bansoko.graphics import Point, Direction, Layer
from bansoko.graphics.animation import AnimationPlayer, Animation
from bansoko.graphics.sprite import Sprite
from bansoko.graphics.tilemap import TilePosition


@dataclass
class GameStats:
    """Statistics of currently played game.

    Attributes:
        game_time - total time spent on playing the level (in ms)
        pushes - number of moves that player made
        steps - number of steps that player made
    """
    game_time = 0.0
    pushes: int = 0
    steps: int = 0


@dataclass
class ObjectPosition:
    """Position of game object in the level.

    Attributes:
        tile_position - game object position in tilemap space
        offset - position offset relative to tile_position (expressed in pixels)
    """
    tile_position: TilePosition
    offset: Point = Point(0, 0)

    def move(self, direction: Direction) -> None:
        """Move object position in given direction by one tile.

        Additionally reset offset.

        :param direction: direction of the movement
        """
        self.tile_position = self.tile_position.move(direction)
        self.offset = Point(0, 0)

    def to_point(self) -> Point:
        """Convert tile position to a point in screen space (taking into account the offset)."""
        return self.tile_position.to_point().offset(self.offset)


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

    def update(self, dt_in_ms: float) -> None:
        """Update game object.

        Called once per frame.

        :param dt_in_ms: delta time since last update (in ms)
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
    """Robot is the main game object, controlled by the player.

    It can move through the level and push crates.

    Attributes:
        face_direction - direction the robot is facing to
        robot_animations - animation pack for all robot states
        animation_player - used for playing robot animations (animation player updated by Robot)
        _robot_state - internal robot's state (used for picking the right animation)
    """
    _robot_state: RobotState

    def __init__(self, tile_position: TilePosition, face_direction: Direction,
                 robot_animations: Dict[RobotState, Animation]):
        super().__init__(tile_position)
        self.face_direction = face_direction
        self.robot_animations = robot_animations
        self.animation_player = AnimationPlayer()
        self.init_state(RobotState.STANDING)

    def init_state(self, robot_state: RobotState, reverse_animation: bool = False) -> None:
        """Initialize robot with given robot state.

        :param robot_state: state to init robot with
        :param reverse_animation: should the animation attached to current state be revered
        """
        self.animation_player.play(self.robot_animations[robot_state], backwards=reverse_animation)
        self._robot_state = robot_state

    def update(self, dt_in_ms: float) -> None:
        self.animation_player.update(dt_in_ms)

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
    """Crate represents a crate game object that can be moved and placed in cargo bays (which is
    the goal of the game)

    Attributes:
        crate_sprites - collection of sprites for all crate states
        state - the state crate is currently in (used for picking the right sprite to draw with and
                importantly to determine whether a crate is in place or not)
    """

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
