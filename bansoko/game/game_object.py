"""Module exposing all game objects."""
import abc
from enum import IntEnum, unique
from typing import Optional

from bansoko.graphics import Point, Direction, Layer
from bansoko.graphics.animation import AnimationPlayer
from bansoko.graphics.sprite import SpritePack
from bansoko.graphics.tilemap import TilePosition, TILE_SIZE


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
        animation_player - update once per frame animation player game object may use
    """
    position: ObjectPosition
    animation_player: AnimationPlayer

    def __init__(self, tile_position: TilePosition) -> None:
        self.position = ObjectPosition(tile_position)
        self.animation_player = AnimationPlayer()

    @property
    def tile_position(self) -> TilePosition:
        """The position in tilemap this game object is located at."""
        return self.position.tile_position

    def update(self) -> None:
        """Update game object.

        Called once per frame.
        """
        self.animation_player.update()

    @abc.abstractmethod
    def draw(self, layer: Layer) -> None:
        """Draw game object on given layer.

        Called once per frame.

        :param layer: layer the game object is drawn on
        """


@unique
class CrateState(IntEnum):
    """Enum defining all states crate can be in.

    Crates can be either PLACED (when they are located in cargo bays) or MISPLACED otherwise.
    """
    MISPLACED = 0
    PLACED = 1


class Crate(GameObject):
    def __init__(self, tile_position: TilePosition, is_placed: bool,
                 crate_sprite_pack: SpritePack) -> None:
        super().__init__(tile_position)
        self.crate_sprite_pack = crate_sprite_pack
        self.state = CrateState.PLACED if is_placed else CrateState.MISPLACED

    @property
    def in_place(self) -> bool:
        """Is the crate placed on a cargo bay tile."""
        return self.state == CrateState.PLACED

    def draw(self, layer: Layer) -> None:
        sprite = self.crate_sprite_pack.sprites[self.state]
        sprite.draw(self.position.to_point(), layer)


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


# TODO: Add animations
class Robot(GameObject):
    def __init__(self, tile_position: TilePosition, face_direction: Direction,
                 robot_sprite_pack: SpritePack):
        super().__init__(tile_position)
        self.face_direction = face_direction
        self.robot_sprite_pack = robot_sprite_pack
        self.state = RobotState.STANDING

    def draw(self, layer: Layer) -> None:
        sprite = self.robot_sprite_pack.sprites[self.state]
        sprite.draw(self.position.to_point(), layer, self.face_direction)


class MoveAction(abc.ABC):
    def __init__(self, game_object: GameObject, direction: Direction, frames_to_complete: int,
                 backward: bool = False):
        self.game_object = game_object
        self.direction = direction
        self.frames_to_complete = frames_to_complete
        self.elapsed_frames = 0
        self.backward = backward

    def update(self, level_stats: MovementStats) -> Optional["MoveAction"]:
        self.elapsed_frames += 1
        move_direction = self.direction.opposite if self.backward else self.direction
        if self.elapsed_frames == self.frames_to_complete:
            self.game_object.position.move(move_direction)
            self._on_stop(level_stats)
            return None

        delta = self.elapsed_frames / self.frames_to_complete * TILE_SIZE
        self.game_object.position.offset = Point(
            int(delta * move_direction.dx), int(delta * move_direction.dy))
        return self

    def reset(self, backward: bool = False) -> None:
        self.elapsed_frames = 0
        self.backward = backward

    def _on_stop(self, level_stats: MovementStats) -> None:
        level_stats.steps += 1 if not self.backward else -1


class MoveRobot(MoveAction):
    """MoveRobot is a move action that encapsulates the movement of robot."""
    def __init__(self, robot: Robot, direction: Direction):
        super().__init__(robot, direction, TILE_SIZE)
        self.robot = robot

    def reset(self, backward: bool = False) -> None:
        super().reset(backward)
        self.robot.face_direction = self.direction
        self.robot.state = RobotState.MOVING


class PushCrate(MoveAction):
    """PushCrate is a move action that encapsulates the movement of robot and the push of crate."""
    def __init__(self, robot: Robot, crate: Crate, direction: Direction) -> None:
        super().__init__(crate, direction, TILE_SIZE)
        self.robot = robot
        self.robot_action = MoveRobot(robot, direction)

    def update(self, level_stats: MovementStats) -> Optional[MoveAction]:
        self.robot_action.update(level_stats)
        return super().update(level_stats)

    def reset(self, backward: bool = False) -> None:
        super().reset(backward)
        self.robot_action.reset(backward)

        # TODO: Refactor robot's state change
        self.robot.state = RobotState.PUSHING

    def _on_stop(self, level_stats: MovementStats) -> None:
        level_stats.pushes += 1 if not self.backward else -1
