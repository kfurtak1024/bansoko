"""Module defining actions that can be executed during game."""
import abc
from typing import Optional

from bansoko import GAME_FRAME_TIME_IN_MS
from bansoko.game.game_object import GameStats, GameObject, Robot, RobotState, Crate
from bansoko.graphics import Direction, Point, TILE_SIZE


class GameAction(abc.ABC):
    """GameAction is a base, abstract class for all game actions.

    Attributes:
        time_to_complete - time after which the action will be completed (in ms)
        elapsed_time - time the action already took (in ms)
        chain_action - secondary, child action that runs along with the action
        backward - is the action running in backward mode (True when we're undo-ing action)
    """

    def __init__(self, time_to_complete: float,
                 chain_action: Optional["GameAction"] = None) -> None:
        self.time_to_complete = time_to_complete
        self.chain_action = chain_action
        self.elapsed_time = 0.0
        self.backward = False

    def update(self, dt_in_ms: float, stats: GameStats) -> Optional["GameAction"]:
        """Update action with given delta time.

        Called once per frame.

        :param dt_in_ms: delta time since last update (in ms)
        :param stats: statistics the action can contribute to
        :return: None if action has complete *OR* self (or any instance of type(self)) otherwise
        """
        if self.chain_action:
            self.chain_action.update(dt_in_ms, stats)
        self.elapsed_time += dt_in_ms
        if self.elapsed_time >= self.time_to_complete:
            self._on_complete(stats)
            return None
        return self

    def reset(self, backward: bool = False) -> None:
        """Reset the action, so it can be executed again.

        :param backward: backward mode the action will be run with (True if we're undo-ing action)
        """
        if self.chain_action:
            self.chain_action.reset(backward=backward)
        self.elapsed_time = 0.0
        self.backward = backward

    def _on_complete(self, stats: GameStats) -> None:
        pass


class MoveAction(GameAction):
    """MoveAction is an abstract class responsible for handling game object movement in tilemap."""

    def __init__(self, game_object: GameObject, direction: Direction,
                 time_to_complete: float, chain_action: Optional[GameAction] = None) -> None:
        super().__init__(time_to_complete, chain_action)
        self.game_object = game_object
        self.direction = direction

    def update(self, dt_in_ms: float, stats: GameStats) -> Optional[GameAction]:
        running_action = super().update(dt_in_ms, stats)
        if running_action:
            move_direction = self.direction.opposite if self.backward else self.direction
            delta = self.elapsed_time / self.time_to_complete * TILE_SIZE
            self.game_object.position.offset = Point(
                int(delta * move_direction.dx), int(delta * move_direction.dy))

        return running_action

    def _on_complete(self, stats: GameStats) -> None:
        move_direction = self.direction.opposite if self.backward else self.direction
        self.game_object.position.move(move_direction)


class TurnRobot(GameAction):
    """TurnRobot is an action for turing the robot in given direction.

    Attributes:
        robot - robot to be turned
        direction - direction to turn the robot in
    """

    def __init__(self, robot: Robot, direction: Direction) -> None:
        super().__init__(time_to_complete=0.0)
        self.robot = robot
        self.direction = direction

    def update(self, dt_in_ms: float, stats: GameStats) -> Optional[GameAction]:
        running_action = super().update(dt_in_ms, stats)
        self.robot.face_direction = self.direction
        return running_action

    def reset(self, backward: bool = False) -> None:
        super().reset(backward=backward)
        self.robot.face_direction = self.direction


TIME_TO_COMPLETE_ROBOT_MOVE = TILE_SIZE * GAME_FRAME_TIME_IN_MS


class MoveRobot(MoveAction):
    """MoveRobot is a move action that encapsulates the movement of robot."""

    def __init__(self, robot: Robot, direction: Direction,
                 move_state: RobotState = RobotState.MOVING):
        super().__init__(robot, direction, TIME_TO_COMPLETE_ROBOT_MOVE, TurnRobot(robot, direction))
        self.robot = robot
        self.move_state = move_state
        self.robot.init_state(move_state)

    def reset(self, backward: bool = False) -> None:
        super().reset(backward)
        self.robot.init_state(self.move_state, reverse_animation=True)

    def _on_complete(self, stats: GameStats) -> None:
        super()._on_complete(stats)
        stats.steps += 1 if not self.backward else -1


TIME_TO_COMPLETE_CRATE_PUSH = TILE_SIZE * GAME_FRAME_TIME_IN_MS


class PushCrate(MoveAction):
    """PushCrate is a move action that encapsulates the movement of robot and the push of crate."""

    def __init__(self, robot: Robot, crate: Crate, direction: Direction) -> None:
        super().__init__(crate, direction, TIME_TO_COMPLETE_CRATE_PUSH,
                         chain_action=MoveRobot(robot, direction, RobotState.PUSHING))
        self.crate = crate

    def _on_complete(self, stats: GameStats) -> None:
        super()._on_complete(stats)
        stats.pushes += 1 if not self.backward else -1
