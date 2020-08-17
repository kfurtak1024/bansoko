from itertools import chain
from typing import List, Iterable, Optional

import pyxel

from game.level import LevelTemplate, LevelStatistics, LEVEL_SIZE, TILE_SIZE
from game.tiles import Direction, TilePosition


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
            self.movement = Movement(direction, 8)

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
        pyxel.rect(x + dx, y + dy, TILE_SIZE, TILE_SIZE, 10)


class Player(GameObject):
    def draw(self) -> None:
        # TODO: Promote coordinates calculation to GameObject
        x = self.tile_position.tile_x * TILE_SIZE
        y = self.tile_position.tile_y * TILE_SIZE
        dx = 0 if not self.movement else self.movement.delta_x()
        dy = 0 if not self.movement else self.movement.delta_y()
        pyxel.rect(x + dx, y + dy, TILE_SIZE, TILE_SIZE, 11)


# TODO: Level should become Game *and* LevelTemplate should become Level?
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
        # TODO: Add offset to tile_map so it will be ideally centered
        self._draw_tilemap(0, 0, 0)
        for game_object in self._game_objects():
            game_object.draw()
        self._draw_tilemap(-1, -1, 1, 0)
        self._draw_tilemap(-2, -2, 2, 0)

    def _game_objects(self) -> Iterable[GameObject]:
        return chain([self.player], self.crates)

    def _draw_tilemap(self, x: int, y: int, tilemap: int, colkey: int = -1):
        pyxel.clip(15, 27, 256 - 15 - 15, 256 - 48 - 27)
        pyxel.bltm(x, y, tilemap, self.level_template.tile_map_u, self.level_template.tile_map_v,
                   LEVEL_SIZE, LEVEL_SIZE, colkey)
        pyxel.clip()
