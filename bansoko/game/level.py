"""Module containing level related classes."""
import abc
from enum import Enum
from itertools import chain
from typing import Optional, List, Iterable, Any, Tuple, NamedTuple

from bansoko.game.core import GameObject, Robot, Crate, RobotState, CrateState
from bansoko.game.tiles import Tileset, TileType
from bansoko.graphics import Point, Direction, Layer, Rect
from bansoko.graphics.sprite import SkinPack
from bansoko.graphics.tilemap import TILE_SIZE, Tilemap, TilePosition

# TODO: Should be taken from bundle
LEVEL_WIDTH = 32
LEVEL_HEIGHT = 32


class LevelStatistics:
    """Player's score for given level.

    Attributes:
        level_num - level number (value from 0 to NUM_LEVELS-1)
        pushes - number of moves that player made
                 ("move" happens when player pushes a crate)
        steps - number of steps that player made
                ("step" happens when player moves by one cell in any direction)
        time_in_ms - time spent playing the level (expressed in milliseconds)
    """

    def __init__(self, level_num: int) -> None:
        self.level_num: int = level_num
        self.pushes: int = 0
        self.steps: int = 0
        self.time_in_ms: int = 0

    @property
    def debug_description(self) -> str:
        # TODO: Just for debug purposes
        hours = int((self.time_in_ms / (1000 * 60 * 60)) % 60)
        minutes = int((self.time_in_ms / (1000 * 60)) % 60)
        seconds = int((self.time_in_ms / 1000) % 60)
        if self.time_in_ms >= 10 * 60 * 60 * 1000:
            hours = 9
            seconds = 59
            minutes = 59

        time = "{:d}:{:02d}:{:02d}".format(hours, minutes, seconds)
        pushes = self.pushes
        steps = self.steps

        return "TIME:   {}\nPUSHES: {:03d}\nSTEPS:  {:03d}".format(time, pushes, steps)

    @property
    def completed(self) -> bool:
        return self.time_in_ms > 0

    def merge_with(self, level_stats: "LevelStatistics") -> None:
        if self == level_stats:
            return
        if self.level_num != level_stats.level_num:
            raise Exception("Cannot merge statistics from different levels")

        if self.completed:
            self.pushes = min(self.pushes, level_stats.pushes)
            self.steps = min(self.steps, level_stats.steps)
            self.time_in_ms = min(self.time_in_ms, level_stats.time_in_ms)
        else:
            self.pushes = level_stats.pushes
            self.steps = level_stats.steps
            self.time_in_ms = level_stats.time_in_ms

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, LevelStatistics):
            return self.level_num == other.level_num and self.pushes == other.pushes \
                   and self.steps == other.steps and self.time_in_ms == other.time_in_ms
        return NotImplemented


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


class LevelTemplate(NamedTuple):
    level_num: int
    tilemap: Tilemap
    tileset: Tileset
    draw_offset: Point
    robot_skin: SkinPack
    crate_skin: SkinPack

    @classmethod
    def from_level_num(cls, level_num: int, tileset_index: int, draw_offset: Point,
                       robot_skin: SkinPack, crate_skin: SkinPack) -> "LevelTemplate":
        tilemap_u = LEVEL_WIDTH * (level_num % TILE_SIZE)
        tilemap_v = LEVEL_HEIGHT * (level_num // TILE_SIZE)
        tilemap = Tilemap(0, Rect.from_coords(tilemap_u, tilemap_v, LEVEL_WIDTH, LEVEL_HEIGHT), 3)
        tileset = Tileset(tileset_index)
        return cls(level_num=level_num, tilemap=tilemap, tileset=tileset, draw_offset=draw_offset,
                   robot_skin=robot_skin, crate_skin=crate_skin)

    def tile_at(self, position: TilePosition) -> TileType:
        return self.tileset.tile_of(self.tilemap.tile_index_at(position))

    def create_layers(self) -> Tuple[Layer, ...]:
        return tuple([Layer(i, self.draw_offset) for i in range(3)])  # TODO: Hard-coded 3!

    def create_crates(self) -> Tuple[Crate, ...]:
        crates_positions = []
        for tile_position in self.tilemap.tiles_positions():
            if self.tile_at(tile_position).is_crate_spawn_point:
                crates_positions.append(tile_position)

        crates = []
        for crate_position in crates_positions:
            is_initially_placed = self.tile_at(crate_position).is_crate_initially_placed
            crates.append(Crate(crate_position, is_initially_placed, self.crate_skin))
        if not crates:
            raise Exception(f"Level {self.level_num} does not have any crates")

        return tuple(crates)

    def create_robot(self, face_direction: Direction) -> Robot:
        start = None
        for tile_position in self.tilemap.tiles_positions():
            if self.tile_at(tile_position).is_start:
                start = tile_position
        if not start:
            raise Exception(f"Level {self.level_num} does not have player start tile")

        return Robot(start, face_direction, self.robot_skin)


class Level:
    def __init__(self, template: LevelTemplate) -> None:
        self.statistics = LevelStatistics(template.level_num)
        self.template = template
        self.layers = template.create_layers()
        self.robot = template.create_robot(self.initial_robot_direction)
        self.crates = template.create_crates()
        self.running_action: Optional[MoveAction] = None
        self.history: List[MoveAction] = []

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
        self.statistics.time_in_ms += 33  # TODO: Hard-coded value! Not accurate!

    def draw(self) -> None:
        """Draw all layers of level in order (from bottom to top)."""
        for layer in self.layers:
            self.template.tilemap.draw(layer)
            for game_object in self.game_objects:
                game_object.draw(layer)

    def _evaluate_crates(self) -> None:
        for crate in self.crates:
            crate_tile = self.template.tile_at(crate.tile_position)
            crate_in_place = crate_tile.is_cargo_bay or crate_tile.is_crate_initially_placed
            crate.state = CrateState.PLACED if crate_in_place else CrateState.MISPLACED
