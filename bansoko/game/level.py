"""Module containing level related classes."""
import abc
from enum import Enum
from itertools import chain
from typing import Optional, List, Iterable

from bansoko import GAME_FRAME_RATE
from bansoko.game.core import GameObject, Robot, Crate, RobotState, CrateState
from bansoko.game.level_template import LevelTemplate
from bansoko.game.profile import LevelScore
from bansoko.graphics import Point, Direction
from bansoko.graphics.tilemap import TILE_SIZE, TilePosition


class LevelStatistics:
    """Player's score for given level.

    Attributes:
        pushes - number of moves that player made
                 ("move" happens when player pushes a crate)
        steps - number of steps that player made
                ("step" happens when player moves by one cell in any direction)
    """

    def __init__(self) -> None:
        self.pushes: int = 0
        self.steps: int = 0


class InputAction(Enum):
    MOVE_LEFT = Direction.LEFT
    MOVE_RIGHT = Direction.RIGHT
    MOVE_UP = Direction.UP
    MOVE_DOWN = Direction.DOWN
    UNDO = None

    def __init__(self, direction: Direction) -> None:
        self.direction = direction

    @property
    def is_movement(self) -> bool:
        """Is this action a movement action."""
        return self.direction is not None


class MoveAction(abc.ABC):
    def __init__(self, game_object: GameObject, direction: Direction, frames_to_complete: int,
                 backward: bool = False):
        self.game_object = game_object
        self.direction = direction
        self.frames_to_complete = frames_to_complete
        self.elapsed_frames = 0
        self.backward = backward

    def update(self, level_stats: LevelStatistics) -> Optional["MoveAction"]:
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

    def _on_stop(self, level_stats: LevelStatistics) -> None:
        level_stats.steps += 1 if not self.backward else -1


class MoveRobot(MoveAction):
    def __init__(self, robot: Robot, direction: Direction):
        super().__init__(robot, direction, TILE_SIZE)
        self.robot = robot

    def reset(self, backward: bool = False) -> None:
        super().reset(backward)
        self.robot.face_direction = self.direction
        self.robot.state = RobotState.MOVING


class PushCrate(MoveAction):
    def __init__(self, robot: Robot, crate: Crate, direction: Direction) -> None:
        super().__init__(crate, direction, TILE_SIZE)
        self.robot = robot
        self.robot_action = MoveRobot(robot, direction)

    def update(self, level_stats: LevelStatistics) -> Optional[MoveAction]:
        self.robot_action.update(level_stats)
        return super().update(level_stats)

    def reset(self, backward: bool = False) -> None:
        super().reset(backward)
        self.robot_action.reset(backward)

        # TODO: Refactor robot's state change
        self.robot.state = RobotState.PUSHING

    def _on_stop(self, level_stats: LevelStatistics) -> None:
        level_stats.pushes += 1 if not self.backward else -1


class Level:
    def __init__(self, template: LevelTemplate) -> None:
        self.statistics = LevelStatistics()
        self.game_time = 0.0
        self.template = template
        self.robot = template.create_robot(self.initial_robot_direction)
        self.crates = template.create_crates()
        self.running_action: Optional[MoveAction] = None
        self.history: List[MoveAction] = []

    @property
    def level_score(self) -> LevelScore:
        return LevelScore(self.template.level_num, self.is_completed, self.statistics.pushes,
                          self.statistics.steps, int(self.game_time))

    @property
    def level_num(self) -> int:
        return self.template.level_num

    @property
    def is_completed(self) -> bool:
        """Test if level objectives are completed.

        Level is completed when all crates are in cargo bays.
        """
        return not next((crate for crate in self.crates if not crate.in_place), None)

    @property
    def initial_robot_direction(self) -> Direction:
        """The initial direction robot is facing to."""
        # TODO: Deduct initial robot direction from level layout
        return Direction.UP

    @property
    def game_objects(self) -> Iterable[GameObject]:
        """Collection of all game objects."""
        return chain([self.robot], self.crates)

    def crate_at_pos(self, position: TilePosition) -> Optional[Crate]:
        """Test if there is a crate at given position.

        :param position: position to test the presence of crate at
        :return: true - if there is a crate in given position *OR* false - otherwise
        """
        return next((crate for crate in self.crates if crate.tile_position == position), None)

    def can_move_crate_to(self, position: TilePosition) -> bool:
        """Test whether a crate can be moved to given position.

        Crate can be moved to a position only when there are no obstacles there (crates, walls).

        :param position: position to test whether the crate can be moved to
        :return: true - if crate can be moved to given location *OR* false - otherwise
        """
        return self.template.tile_at(position).is_walkable and not self.crate_at_pos(position)

    def process_input(self, input_action: Optional[InputAction]) -> None:
        """Transform given input action to game action and queue it (so it can be run later,
        during update call)."""

        if self.running_action:
            # TODO: Add movement cancellation when movement with opposite direction was triggered
            #       (only when robot is not pushing a crate)
            return

        # TODO: If player is pressing more then one directional button, prefer the one which
        #       does not lead to collision

        self.robot.state = RobotState.STANDING

        if not input_action:
            return

        if input_action == InputAction.UNDO and self.history:
            self.running_action = self.history.pop()
            self.running_action.reset(backward=True)
        if input_action.is_movement:
            self.robot.face_direction = input_action.direction
            robot_dest = self.robot.tile_position.move(input_action.direction)
            if self.template.tile_at(robot_dest).is_walkable:
                crate = self.crate_at_pos(robot_dest)
                if crate:
                    crate_dest = crate.tile_position.move(input_action.direction)
                    if self.can_move_crate_to(crate_dest):
                        self.running_action = PushCrate(self.robot, crate, input_action.direction)
                else:
                    self.running_action = MoveRobot(self.robot, input_action.direction)

                if self.running_action:
                    self.running_action.reset()
                    self.history.append(self.running_action)

    def update(self) -> None:
        """Perform an update on the level's game logic."""
        if self.running_action:
            self.running_action = self.running_action.update(self.statistics)
        self._evaluate_crates()
        self.game_time += 1_000 / GAME_FRAME_RATE

    def draw(self) -> None:
        """Draw all layers of level in order (from bottom to top)."""
        for layer in self.template.layers:
            self.template.tilemap.draw(layer)
            for game_object in self.game_objects:
                game_object.draw(layer)

    def _evaluate_crates(self) -> None:
        for crate in self.crates:
            crate_tile = self.template.tile_at(crate.tile_position)
            crate_in_place = crate_tile.is_cargo_bay or crate_tile.is_crate_initially_placed
            crate.state = CrateState.PLACED if crate_in_place else CrateState.MISPLACED
