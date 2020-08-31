"""Module containing level related classes."""
import abc
from enum import Enum
from itertools import chain
from typing import Optional, List, Iterable

import pyxel

from bansoko.game.core import GameObject, Robot, Crate, RobotState, CrateState
from bansoko.game.tiles import Tileset, Tilemap, LEVEL_WIDTH, LEVEL_HEIGHT, TILE_SIZE, TilePosition
from bansoko.graphics import Point, Direction, Layer
from bansoko.graphics.sprite import SkinPack


class LevelStatistics:
    """
    Player's score for given level.

    Attributes:
        level_num - level number (value from 0 to NUM_LEVELS-1)
        pushes - number of moves that player made
                 ("move" happens when player pushes a crate)
        steps - number of steps that player made
                ("step" happens when player moves by one cell in any direction)
        time_in_ms - time spent playing the level (expressed in milliseconds)
    """

    def __init__(self, level_num: int):
        self.level_num: int = level_num
        self.pushes: int = 0
        self.steps: int = 0
        self.time_in_ms: int = 0


# TODO: Is it needed in this form?
class LevelTemplate:
    level_num: int
    tilemap: Tilemap

    def __init__(self, level_num: int, theme_index: int):
        tilemap_u = LEVEL_WIDTH * (level_num % TILE_SIZE)
        tilemap_v = LEVEL_HEIGHT * (level_num // TILE_SIZE)
        self.level_num = level_num
        self.tilemap = Tilemap(Tileset(theme_index), tilemap_u, tilemap_v)


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

    def reset(self, backward: bool = False):
        self.elapsed_frames = 0
        self.backward = backward

    def _on_stop(self, level_stats: LevelStatistics) -> None:
        level_stats.steps += 1 if not self.backward else -1


class MoveRobot(MoveAction):
    def __init__(self, robot: Robot, direction: Direction):
        super().__init__(robot, direction, TILE_SIZE)
        self.robot = robot

    def reset(self, backward: bool = False):
        super().reset(backward)
        self.robot.face_direction = self.direction
        self.robot.state = RobotState.MOVING


class PushCrate(MoveAction):
    def __init__(self, robot: Robot, crate: Crate, direction: Direction):
        super().__init__(crate, direction, TILE_SIZE)
        self.robot = robot
        self.robot_action = MoveRobot(robot, direction)

    def update(self, level_stats: LevelStatistics) -> Optional[MoveAction]:
        self.robot_action.update(level_stats)
        return super().update(level_stats)

    def reset(self, backward: bool = False):
        super().reset(backward)
        self.robot_action.reset(backward)

        # TODO: Refactor robot's state change
        self.robot.state = RobotState.PUSHING

    def _on_stop(self, level_stats: LevelStatistics) -> None:
        level_stats.pushes += 1 if not self.backward else -1


class Level:
    def __init__(self, level_template: LevelTemplate, robot_skin: SkinPack, crate_skin: SkinPack):
        tilemap = level_template.tilemap

        self.statistics = LevelStatistics(level_template.level_num)
        self.tilemap = tilemap
        self.robot = Robot(self.tilemap.start, self.initial_robot_direction, robot_skin)
        self.crates = [
            Level.__new_crate(position, tilemap, crate_skin) for position in self.tilemap.crates
        ]
        self.running_action: Optional[MoveAction] = None
        self.history: List[MoveAction] = []

    @property
    def is_completed(self) -> bool:
        return not next((crate for crate in self.crates if not crate.in_place), None)

    @property
    def initial_robot_direction(self) -> Direction:
        # TODO: Deduct initial robot direction from level layout
        return Direction.UP

    @property
    def game_objects(self) -> Iterable[GameObject]:
        return chain([self.robot], self.crates)

    def crate_at_pos(self, position: TilePosition) -> Optional[Crate]:
        return next((crate for crate in self.crates if crate.tile_position == position), None)

    def can_move_crate_to(self, position: TilePosition) -> bool:
        return self.tilemap.tile_at(position).is_walkable and not self.crate_at_pos(position)

    def process_input(self, input_action: Optional[InputAction]) -> None:
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
            if self.tilemap.tile_at(robot_dest).is_walkable:
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
        if self.running_action:
            self.running_action = self.running_action.update(self.statistics)
        self.__evaluate_crates()
        self.statistics.time_in_ms += 33  # TODO: Hard-coded value!

    def draw(self) -> None:
        # TODO: Add offset to tilemap so it will be ideally centered
        for layer in list(Layer):
            self.__draw_level_layer(layer)

    @staticmethod
    def __new_crate(position: TilePosition, tilemap: Tilemap, crate_skin: SkinPack) -> Crate:
        is_initially_placed = tilemap.tile_at(position).is_crate_initially_placed
        return Crate(position, is_initially_placed, crate_skin)

    def __evaluate_crates(self) -> None:
        for crate in self.crates:
            crate_tile = self.tilemap.tile_at(crate.tile_position)
            crate_in_place = crate_tile.is_cargo_bay or crate_tile.is_crate_initially_placed
            crate.state = CrateState.PLACED if crate_in_place else CrateState.MISPLACED

    def __draw_level_layer(self, layer: Layer) -> None:
        # TODO: This clip() is temporary
        pyxel.clip(15, 27, 256 - 15 - 15, 256 - 48 - 27)
        pyxel.bltm(layer.offset.x, layer.offset.y, layer.layer_index,
                   self.tilemap.u, self.tilemap.v, LEVEL_WIDTH, LEVEL_HEIGHT,
                   colkey=-1 if layer.is_main else 0)
        for game_object in self.game_objects:
            game_object.draw(layer)
        pyxel.clip()
