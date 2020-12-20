"""Module containing level related classes."""
from enum import Enum
from itertools import chain
from typing import Optional, List, Iterable

from bansoko.game.game_action import GameAction, PushCrate, MoveRobot, TurnRobot
from bansoko.game.game_object import GameObject, Crate, RobotState, CrateState, GameStats
from bansoko.game.level_template import LevelTemplate
from bansoko.game.profile import LevelScore
from bansoko.graphics import Direction
from bansoko.graphics.tilemap import TilePosition


class InputAction(Enum):
    """InputAction represents all possible actions player can perform when playing a level."""
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


class Level:
    """Level encapsulates the game logic for playing a level.

    It draws the level with all game objects, it handles the input (used for controlling Robot) and
    it evaluates victory condition.

    Attributes:
        statistics - statistics captures during the play of the level
        template - template the level is crated from
        robot - instance of Robot game object, that player can control
        crates - collection of all Crate game objects for the level
        running_action - currently running game action (updated in update method)
        last_input_action - input action that triggered running_action
        history - list of historical game actions (used for undo)
    """

    def __init__(self, template: LevelTemplate) -> None:
        self.statistics = GameStats()
        self.template = template
        self.robot = template.create_robot()
        self.crates = template.create_crates()
        self.running_action: Optional[GameAction] = None
        self.last_input_action: Optional[InputAction] = None
        self.history: List[GameAction] = []

    @property
    def level_score(self) -> LevelScore:
        """Current player's score in the level."""
        return LevelScore(self.template.level_num, self.is_completed, self.statistics.pushes,
                          self.statistics.steps, int(self.statistics.game_time))

    @property
    def level_num(self) -> int:
        """The number of the level."""
        return self.template.level_num

    @property
    def is_completed(self) -> bool:
        """Test if level objectives are completed.

        Level is completed when all crates are in cargo bays.
        """
        return not next((crate for crate in self.crates if not crate.in_place), None)

    @property
    def game_objects(self) -> Iterable[GameObject]:
        """Collection of all game objects."""
        return chain([self.robot], self.crates)

    def crate_at_pos(self, position: TilePosition) -> Optional[Crate]:
        """Test if there is a crate at given position.

        :param position: position to test the presence of crate at
        :return: True - if there is a crate in given position *OR* False - otherwise
        """
        return next((crate for crate in self.crates if crate.tile_position == position), None)

    def can_move_crate_to(self, position: TilePosition) -> bool:
        """Test whether a crate can be moved to given position.

        Crate can be moved to a position only when there are no obstacles there (crates, walls).

        :param position: position to test whether the crate can be moved to
        :return: True - if crate can be moved to given location *OR* False - otherwise
        """
        return self.template.tile_at(position).is_walkable and not self.crate_at_pos(position)

    def is_crate_in_place(self, position: TilePosition) -> bool:
        """Test whether the crate is "in place" (at cargo bay) in given position.

        :param position: position to test whether the crate is "in place" or not
        :return: True - if crate is "in place" at given position *OR* False - otherwise
        """
        tile = self.template.tile_at(position)
        return tile.is_cargo_bay or tile.is_crate_initially_placed

    def process_input(self, input_action: Optional[InputAction]) -> None:
        """Transform given input action to game action and queue it (so it can be run later,
        during update call)."""

        if self.running_action:
            # TODO: Add movement cancellation when movement with opposite direction was triggered
            #       (only when robot is not pushing a crate)
            return

        # TODO: If player is pressing more then one directional button, prefer the one which
        #       does not lead to collision

        # Before checking the input we don't know whether there will be a continuation of the
        # movement or not. That's why we cannot put robot to standing state when action finishes.
        # We have to do it here. The same applies to last_input_action.
        self.robot.init_state(RobotState.STANDING)
        self.last_input_action = input_action

        if not input_action:
            return

        if input_action == InputAction.UNDO and self.history:
            self.running_action = self.history.pop()
            self.running_action.reset(backward=True)
        if input_action.is_movement:
            robot_dest = self.robot.tile_position.move(input_action.direction)
            if self.template.tile_at(robot_dest).is_walkable:
                crate = self.crate_at_pos(robot_dest)
                if crate:
                    crate_dest = crate.tile_position.move(input_action.direction)
                    if self.can_move_crate_to(crate_dest):
                        self.running_action = PushCrate(self.robot, crate, input_action.direction)
                else:
                    self.running_action = MoveRobot(self.robot, input_action.direction)
            else:
                self.running_action = TurnRobot(self.robot, input_action.direction)

    def update(self, dt_in_ms: float) -> None:
        """Perform an update on the level's game logic."""
        self._update_running_action(dt_in_ms)
        self._evaluate_crates()
        for game_object in self.game_objects:
            game_object.update(dt_in_ms)
        self.statistics.game_time += dt_in_ms

    def draw(self) -> None:
        """Draw all layers of level in order (from bottom to top)."""
        for layer in self.template.layers:
            self.template.tilemap.draw(layer)
            for game_object in self.game_objects:
                game_object.draw(layer)

    def _update_running_action(self, dt_in_ms: float) -> None:
        if self.running_action:
            last_action = self.running_action
            self.running_action = self.running_action.update(dt_in_ms, self.statistics)

            if last_action is not self.running_action and not last_action.backward:
                self.history.append(last_action)

    def _evaluate_crates(self) -> None:
        for crate in self.crates:
            crate_in_place = self.is_crate_in_place(crate.tile_position)
            crate.state = CrateState.PLACED if crate_in_place else CrateState.MISPLACED
