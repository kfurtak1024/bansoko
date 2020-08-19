from itertools import chain
from typing import List, Iterable, Optional

import pyxel

from bansoko.game.level import LevelTemplate, LevelStatistics, TILE_SIZE, LEVEL_HEIGHT, LEVEL_WIDTH, \
    LevelLayer
from bansoko.game.tiles import Direction, TilePosition


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

    def draw(self, layer: LevelLayer) -> None:
        pass


class Crate(GameObject):
    in_place: bool = False

    def draw(self, layer: LevelLayer) -> None:
        # TODO: Promote coordinates calculation to GameObject
        x = self.tile_position.tile_x * TILE_SIZE
        y = self.tile_position.tile_y * TILE_SIZE
        dx = 0 if not self.movement else self.movement.delta_x()
        dy = 0 if not self.movement else self.movement.delta_y()
        # TODO: Add sprite for crates
        pyxel.rect(x + dx + layer.offset.x, y + dy + layer.offset.y, TILE_SIZE, TILE_SIZE, 10)


class Player(GameObject):
    def draw(self, layer: LevelLayer) -> None:
        # TODO: Promote coordinates calculation to GameObject
        x = self.tile_position.tile_x * TILE_SIZE
        y = self.tile_position.tile_y * TILE_SIZE
        dx = 0 if not self.movement else self.movement.delta_x()
        dy = 0 if not self.movement else self.movement.delta_y()
        # TODO: Add sprite for player
        pyxel.rect(x + dx + layer.offset.x, y + dy + layer.offset.x, TILE_SIZE, TILE_SIZE, 11)


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
        for game_object in self.game_objects:
            game_object.update()

    def draw(self) -> None:
        # TODO: Add offset to tile_map so it will be ideally centered
        for layer in list(LevelLayer):
            self.__draw_level_layer(layer)

    @property
    def game_objects(self) -> Iterable[GameObject]:
        return chain([self.player], self.crates)

    def __draw_level_layer(self, layer: LevelLayer) -> None:
        # TODO: This clip() is temporary
        pyxel.clip(15, 27, 256 - 15 - 15, 256 - 48 - 27)
        pyxel.bltm(layer.offset.x,
                   layer.offset.y,
                   layer.layer_index,
                   self.level_template.tile_map_u,
                   self.level_template.tile_map_v,
                   LEVEL_WIDTH,
                   LEVEL_HEIGHT,
                   colkey=-1 if layer.is_main else 0)
        for game_object in self.game_objects:
            game_object.draw(layer)
        pyxel.clip()
