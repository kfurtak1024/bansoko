import abc
from itertools import chain
from typing import Iterable, Optional

import pyxel

from bansoko.game.level import LevelTemplate, LevelStatistics, LevelLayer
from bansoko.game.tiles import Direction, TilePosition, TILE_SIZE, LEVEL_WIDTH, \
    LEVEL_HEIGHT
from bansoko.graphics import Point


class Movement:
    # TODO: Rethink the whole Movement class
    # TODO: Those should be floats!
    def __init__(self, direction: Direction, frames_to_complete: int):
        self.direction = direction
        self.frames_to_complete = frames_to_complete
        self.delta = TilePosition(0, 0).move(direction)
        self.elapsed_frames = 0

    @property
    def delta_x(self) -> int:
        return int(self.elapsed_frames * self.delta.tile_x / self.frames_to_complete * TILE_SIZE)

    @property
    def delta_y(self) -> int:
        return int(self.elapsed_frames * self.delta.tile_y / self.frames_to_complete * TILE_SIZE)


class GameObject(abc.ABC):
    tile_position: TilePosition
    movement: Optional[Movement]

    def __init__(self, tile_position: TilePosition):
        self.tile_position = tile_position
        self.movement = None

    @property
    def is_moving(self) -> bool:
        return self.movement is not None

    def position(self, layer: LevelLayer) -> Point:
        dx = 0 if not self.movement else self.movement.delta_x
        dy = 0 if not self.movement else self.movement.delta_y
        position = self.tile_position.to_point()
        return Point(position.x + dx + layer.offset.x, position.y + dy + layer.offset.y)

    def move(self, direction: Direction) -> None:
        if not self.is_moving:
            self.movement = Movement(direction, TILE_SIZE)

    def update(self) -> None:
        # TODO: Refactor this!
        if self.movement:
            self.movement.elapsed_frames += 1
            if self.movement.elapsed_frames == self.movement.frames_to_complete:
                self.tile_position = self.tile_position.move(self.movement.direction)
                self.movement = None

    def draw(self, layer: LevelLayer) -> None:
        self._do_draw(self.position(layer))

    @abc.abstractmethod
    def _do_draw(self, position: Point) -> None:
        pass


class Crate(GameObject):
    def __init__(self, tile_position: TilePosition):
        super().__init__(tile_position)
        self.in_place = False

    def _do_draw(self, position: Point) -> None:
        # TODO: Add sprite for crates
        pyxel.rect(position.x, position.y, TILE_SIZE, TILE_SIZE, 3 if self.in_place else 8)


class Player(GameObject):
    def __init__(self, tile_position: TilePosition):
        super().__init__(tile_position)
        self.is_pushing = False

    def _do_draw(self, position: Point) -> None:
        # TODO: Add sprite for player
        pyxel.rect(position.x, position.y, TILE_SIZE, TILE_SIZE, 12 if self.is_pushing else 1)


# TODO: Move it to level module again?
class Level:
    def __init__(self, level_template: LevelTemplate):
        self.statistics = LevelStatistics(level_template.level_num)
        self.tilemap = level_template.tilemap
        self.crates = [Crate(position) for position in self.tilemap.crates]
        self.player = Player(self.tilemap.player_start)
        self.player_movement: Optional[Direction] = None

    @property
    def is_completed(self) -> bool:
        return not next((crate for crate in self.crates if not crate.in_place), None)

    @property
    def game_objects(self) -> Iterable[GameObject]:
        return chain([self.player], self.crates)

    def post_player_movement(self, direction: Optional[Direction]) -> None:
        self.player_movement = direction

    def crate_at_pos(self, position: TilePosition) -> Optional[Crate]:
        return next((crate for crate in self.crates if crate.tile_position == position), None)

    def can_move_crate_to(self, position: TilePosition) -> bool:
        return self.tilemap.tile_at(position).is_walkable and not self.crate_at_pos(position)

    def update(self) -> None:
        self.__move_player()
        self.__clear_player_movement()
        for game_object in self.game_objects:
            game_object.update()
        self.__evaluate_crates()

    def draw(self) -> None:
        # TODO: Add offset to tilemap so it will be ideally centered
        for layer in list(LevelLayer):
            self.__draw_level_layer(layer)

    def __move_player(self) -> None:
        if self.player.is_moving:
            return

        # TODO: Add movement cancellation when movement with opposite direction was triggered
        #       (only when player is not pushing a crate)

        # TODO: If player is pressing more then one directional button, prefer the one which
        #       does not lead to collision

        self.player.is_pushing = False

        if not self.player_movement:
            return

        player_dest = self.player.tile_position.move(self.player_movement)
        if self.tilemap.tile_at(player_dest).is_walkable:
            # TODO: Add logic for moving crates
            crate = self.crate_at_pos(player_dest)
            if crate:
                crate_dest = crate.tile_position.move(self.player_movement)
                if self.can_move_crate_to(crate_dest):
                    crate.move(self.player_movement)
                    self.player.move(self.player_movement)
                    self.player.is_pushing = True
            else:
                self.player.move(self.player_movement)

    def __clear_player_movement(self) -> None:
        self.player_movement = None

    def __evaluate_crates(self) -> None:
        for crate in self.crates:
            crate_tile = self.tilemap.tile_at(crate.tile_position)
            crate.in_place = crate_tile.is_cargo_bay or crate_tile.is_crate_initially_placed

    def __draw_level_layer(self, layer: LevelLayer) -> None:
        # TODO: This clip() is temporary
        pyxel.clip(15, 27, 256 - 15 - 15, 256 - 48 - 27)
        pyxel.bltm(layer.offset.x, layer.offset.y, layer.layer_index,
                   self.tilemap.u, self.tilemap.v, LEVEL_WIDTH, LEVEL_HEIGHT,
                   colkey=-1 if layer.is_main else 0)
        for game_object in self.game_objects:
            game_object.draw(layer)
        pyxel.clip()
