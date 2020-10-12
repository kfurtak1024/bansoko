import abc
from typing import Optional

from bansoko.game.game_object import MovementStats, GameObject, Robot, RobotState, Crate
from bansoko.graphics import Direction, Point
from bansoko.graphics.tilemap import TILE_SIZE


class Action(abc.ABC):
    def __init__(self) -> None:
        self.backward = False

    @abc.abstractmethod
    def update(self, dt_in_ms: float, movement_stats: MovementStats) -> Optional["Action"]:
        pass

    def reset(self, backward: bool = False) -> None:
        self.backward = backward


class MoveAction(Action):
    """MoveAction is an abstract class responsible for handling game object movement in tilemap."""
    def __init__(self, game_object: GameObject, direction: Direction, frames_to_complete: int):
        super().__init__()
        self.game_object = game_object
        self.direction = direction

        # TODO: It should be time_to_complete
        self.frames_to_complete = frames_to_complete

        # TODO: Promote both elapsed_frames and frames_to_complete to Action
        self.elapsed_frames = 0

    def update(self, dt_in_ms: float, movement_stats: MovementStats) -> Optional[Action]:
        self.elapsed_frames += 1
        move_direction = self.direction.opposite if self.backward else self.direction
        if self.elapsed_frames == self.frames_to_complete:
            self.game_object.position.move(move_direction)
            self._on_stop(movement_stats)
            return None

        delta = self.elapsed_frames / self.frames_to_complete * TILE_SIZE
        self.game_object.position.offset = Point(
            int(delta * move_direction.dx), int(delta * move_direction.dy))
        return self

    def reset(self, backward: bool = False) -> None:
        super().reset(backward)
        # TODO: It should be elapsed_time
        self.elapsed_frames = 0

    def _on_stop(self, movement_stats: MovementStats) -> None:
        pass


class TurnRobot(Action):
    def __init__(self, robot: Robot, direction: Direction) -> None:
        super().__init__()
        self.robot = robot
        self.direction = direction

    def update(self, dt_in_ms: float, movement_stats: MovementStats) -> Optional[Action]:
        self.robot.face_direction = self.direction
        return None

    def reset(self, backward: bool = False) -> None:
        super().reset(backward=backward)
        self.robot.face_direction = self.direction


# TODO: Refactor all move actions!
class MoveRobot(MoveAction):
    """MoveRobot is a move action that encapsulates the movement of robot."""

    def __init__(self, robot: Robot, direction: Direction,
                 robot_state: RobotState = RobotState.MOVING):
        super().__init__(robot, direction, TILE_SIZE)
        self.turn_robot_action = TurnRobot(robot, direction)
        self.robot = robot
        # TODO: Rename it!
        self.robot_state = robot_state

        self.robot.robot_state = robot_state

    def update(self, dt_in_ms: float, movement_stats: MovementStats) -> Optional[Action]:
        self.turn_robot_action.update(dt_in_ms, movement_stats)
        return super().update(dt_in_ms, movement_stats)

    def reset(self, backward: bool = False) -> None:
        super().reset(backward)
        self.turn_robot_action.reset(backward=backward)
        self.robot.robot_state = self.robot_state
        # TODO: What about animation when moving backward?

    def _on_stop(self, movement_stats: MovementStats) -> None:
        movement_stats.steps += 1 if not self.backward else -1


class PushCrate(MoveAction):
    """PushCrate is a move action that encapsulates the movement of robot and the push of crate."""
    def __init__(self, robot: Robot, crate: Crate, direction: Direction) -> None:
        super().__init__(crate, direction, TILE_SIZE)
        self.move_robot_action = MoveRobot(robot, direction, RobotState.PUSHING)
        self.crate = crate

    def update(self, dt_in_ms: float, movement_stats: MovementStats) -> Optional[Action]:
        self.move_robot_action.update(dt_in_ms, movement_stats)
        return super().update(dt_in_ms, movement_stats)

    def reset(self, backward: bool = False) -> None:
        super().reset(backward)
        self.move_robot_action.reset(backward=backward)

    def _on_stop(self, movement_stats: MovementStats) -> None:
        movement_stats.pushes += 1 if not self.backward else -1
