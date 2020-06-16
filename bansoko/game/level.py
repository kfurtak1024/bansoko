"""
Module containing level related classes.
"""
from enum import Enum, unique
from itertools import chain
from typing import NamedTuple, Iterable, Optional, List

import pyxel

NUM_LEVELS: int = 60
LEVEL_SIZE = 32
TILE_SIZE = 8


@unique
class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class LevelStatistics(NamedTuple):
    """
    Player's score for given level.

    Attributes:
        level_num - level number (value from 0 to NUM_LEVELS-1)
        moves - number of moves that player made
                ("move" happens when player pushes a crate)
        steps - number of steps that player made
                ("step" happens when player moves by one cell in any direction)
        time - time spent playing the level
    """

    level_num: int
    moves: int = 0
    steps: int = 0
    time: int = 0


class TilePosition(NamedTuple):
    tile_x: int = 0
    tile_y: int = 0

    def move(self, direction: Direction):
        destination_x = self.tile_x
        destination_y = self.tile_y
        # TODO: Can I move it to Direction enum?
        if direction is Direction.UP:
            destination_y -= 1
        elif direction is Direction.DOWN:
            destination_y += 1
        elif direction is Direction.LEFT:
            destination_x -= 1
        elif direction is Direction.RIGHT:
            destination_x += 1
        return TilePosition(destination_x, destination_y)


class Movement:
    # TODO: Rethink the whole Movement class
    dx: int = 0
    dy: int = 0

    def __init__(self, direction: Direction, frames_to_complete: int):
        self.direction = direction
        self.frames_to_complete = frames_to_complete
        self.delta = TilePosition(0, 0).move(direction)
        self.elapsed_frames = 0

    def delta_x(self) -> int:
        return int(self.elapsed_frames * self.delta.tile_x / self.frames_to_complete * TILE_SIZE)

    def delta_y(self) -> int:
        return int(self.elapsed_frames * self.delta.tile_y / self.frames_to_complete * TILE_SIZE)


class GameObject:
    tile_position: TilePosition
    movement: Optional[Movement] = None

    def __init__(self, tile_position: TilePosition):
        self.tile_position = tile_position

    def is_moving(self) -> bool:
        return self.movement is not None

    def move(self, direction: Direction) -> None:
        if not self.is_moving():
            # TODO: Hard-coded value
            self.movement = Movement(direction, 10)

    def update(self) -> None:
        # TODO: Refactor this!
        if self.movement:
            self.movement.elapsed_frames += 1
            if self.movement.elapsed_frames == self.movement.frames_to_complete:
                self.tile_position = self.tile_position.move(self.movement.direction)
                self.movement = None

    def draw(self) -> None:
        pass


class Crate(GameObject):
    in_place: bool = False

    def draw(self) -> None:
        # TODO: Promote coordinates calculation to GameObject
        x = self.tile_position.tile_x * TILE_SIZE
        y = self.tile_position.tile_y * TILE_SIZE
        dx = 0 if not self.movement else self.movement.delta_x()
        dy = 0 if not self.movement else self.movement.delta_y()
        pyxel.rect(x + dx, y + dy, TILE_SIZE, TILE_SIZE, 8)


class Player(GameObject):
    def draw(self) -> None:
        # TODO: Promote coordinates calculation to GameObject
        x = self.tile_position.tile_x * TILE_SIZE
        y = self.tile_position.tile_y * TILE_SIZE
        dx = 0 if not self.movement else self.movement.delta_x()
        dy = 0 if not self.movement else self.movement.delta_y()
        pyxel.rect(x + dx, y + dy, TILE_SIZE, TILE_SIZE, 12)


class LevelTemplate:
    level_num: int
    player_pos: TilePosition
    crates_pos: List[TilePosition]

    def __init__(self, level_num: int):
        self.level_num = level_num
        self.crates_pos = []
        tile_map = pyxel.tilemap(0)
        tile_map_u = self.tile_map_u
        tile_map_v = self.tile_map_v
        for u in range(tile_map_u, tile_map_u + LEVEL_SIZE):
            for v in range(tile_map_v, tile_map_v + LEVEL_SIZE):
                tile = tile_map.get(u, v)
                position = TilePosition(u - tile_map_u, v - tile_map_v)
                if self.__is_crate_tile(tile):
                    self.crates_pos.append(position)
                elif self.__is_player_start_tile(tile):
                    self.player_pos = position

    @property
    def tile_map_u(self) -> int:
        return LEVEL_SIZE * (self.level_num % TILE_SIZE)

    @property
    def tile_map_v(self) -> int:
        return LEVEL_SIZE * (self.level_num // TILE_SIZE)

    @staticmethod
    def __is_crate_tile(tile: int):
        # TODO: Read it from resources file (instead of hard-coded value)
        return tile in [4, 5]

    @staticmethod
    def __is_player_start_tile(tile: int):
        # TODO: Read it from resources file (instead of hard-coded value)
        return tile == 2


class Level:
    level_template: LevelTemplate
    statistics: LevelStatistics
    crates: List[Crate]
    player: Player

    def __init__(self, level_template: LevelTemplate):
        self.level_template = level_template
        self.statistics = LevelStatistics(level_template.level_num)
        self.crates = [Crate(position) for position in level_template.crates_pos]
        self.player = Player(level_template.player_pos)

    def is_completed(self) -> bool:
        misplaced_crates = [crate for crate in self.crates if not crate.in_place]
        return not misplaced_crates

    def move_player(self, direction: Direction) -> None:
        if self.player.is_moving():
            return
        # TODO: Add logic for moving crates
        self.player.move(direction)

    def update(self) -> None:
        for game_object in self._game_objects():
            game_object.update()

    def draw(self) -> None:
        pyxel.bltm(0, 0, 0, self.level_template.tile_map_u, self.level_template.tile_map_v,
                   LEVEL_SIZE, LEVEL_SIZE)
        for game_object in self._game_objects():
            game_object.draw()

    def _game_objects(self) -> Iterable[GameObject]:
        return chain([self.player], self.crates)
