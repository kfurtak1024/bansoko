import abc
from enum import Enum
from itertools import chain
from typing import Iterable, Optional, List

import pyxel

from bansoko.game.level import LevelTemplate, LevelStatistics, LevelLayer
from bansoko.game.tiles import Direction, TilePosition, TILE_SIZE, LEVEL_WIDTH, \
    LEVEL_HEIGHT
from bansoko.graphics import Point


class InputAction(Enum):
    MOVE_LEFT = Direction.LEFT
    MOVE_RIGHT = Direction.RIGHT
    MOVE_UP = Direction.UP
    MOVE_DOWN = Direction.DOWN
    UNDO = None

    def __init__(self, direction: Direction):
        self.direction = direction

    def is_movement(self):
        return self.direction


class ObjectPosition:
    tile_position: TilePosition
    offset: Point

    def __init__(self, tile_position: TilePosition):
        self.tile_position = tile_position
        self.offset = Point(0, 0)

    def move(self, direction: Direction) -> None:
        self.tile_position = self.tile_position.move(direction)
        self.offset = Point(0, 0)

    def to_point(self) -> Point:
        return self.tile_position.to_point().offset(self.offset.x, self.offset.y)


class GameObject(abc.ABC):
    position: ObjectPosition

    def __init__(self, tile_position: TilePosition):
        self.position = ObjectPosition(tile_position)

    @property
    def tile_position(self) -> TilePosition:
        return self.position.tile_position

    def position_on_layer(self, layer: LevelLayer) -> Point:
        return self.position.to_point().offset(layer.offset.x, layer.offset.y)

    def draw(self, layer: LevelLayer) -> None:
        self._do_draw(self.position_on_layer(layer))

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


class MoveAction(abc.ABC):
    def __init__(self, game_object: GameObject, direction: Direction, frames_to_complete: int):
        self.game_object = game_object
        self.direction = direction
        self.frames_to_complete = frames_to_complete
        self.elapsed_frames = 0

    def update(self) -> Optional["MoveAction"]:
        self.elapsed_frames += 1
        if self.elapsed_frames == self.frames_to_complete:
            self.game_object.position.move(self.direction)
            return None

        delta = self.elapsed_frames / self.frames_to_complete * TILE_SIZE
        self.game_object.position.offset = Point(
            int(delta * self.direction.dx), int(delta * self.direction.dy))
        return self


class MovePlayer(MoveAction):
    def __init__(self, player: Player, direction: Direction):
        super().__init__(player, direction, TILE_SIZE)


class PushCrate(MoveAction):
    def __init__(self, player: Player, crate: Crate, direction: Direction):
        super().__init__(crate, direction, TILE_SIZE)
        self.player_action = MovePlayer(player, direction)

    def update(self) -> Optional[MoveAction]:
        self.player_action.update()
        return super().update()


# TODO: Move it to level module again?
class Level:
    def __init__(self, level_template: LevelTemplate):
        self.statistics = LevelStatistics(level_template.level_num)
        self.tilemap = level_template.tilemap
        self.player = Player(self.tilemap.player_start)
        self.crates = [Crate(position) for position in self.tilemap.crates]
        self.running_action: Optional[MoveAction] = None
        self.history: List[MoveAction] = []

    @property
    def is_completed(self) -> bool:
        return not next((crate for crate in self.crates if not crate.in_place), None)

    @property
    def game_objects(self) -> Iterable[GameObject]:
        return chain([self.player], self.crates)

    def crate_at_pos(self, position: TilePosition) -> Optional[Crate]:
        return next((crate for crate in self.crates if crate.tile_position == position), None)

    def can_move_crate_to(self, position: TilePosition) -> bool:
        return self.tilemap.tile_at(position).is_walkable and not self.crate_at_pos(position)

    def process_input(self, input_action: Optional[InputAction]) -> None:
        if self.running_action:
            # TODO: Add movement cancellation when movement with opposite direction was triggered
            #       (only when player is not pushing a crate)
            return

        # TODO: If player is pressing more then one directional button, prefer the one which
        #       does not lead to collision

        self.player.is_pushing = False

        if not input_action:
            return

        if input_action == InputAction.UNDO:
            # TODO: Not implemented yet!
            self.running_action = self.history.pop() if self.history else None
        elif input_action.is_movement():
            player_dest = self.player.tile_position.move(input_action.direction)
            if self.tilemap.tile_at(player_dest).is_walkable:
                crate = self.crate_at_pos(player_dest)
                if crate:
                    crate_dest = crate.tile_position.move(input_action.direction)
                    if self.can_move_crate_to(crate_dest):
                        self.running_action = PushCrate(self.player, crate, input_action.direction)
                        self.player.is_pushing = True
                else:
                    self.running_action = MovePlayer(self.player, input_action.direction)

                if self.running_action:
                    self.history.append(self.running_action)

    def update(self) -> None:
        self.running_action = self.running_action.update() if self.running_action else None
        self.__evaluate_crates()

    def draw(self) -> None:
        # TODO: Add offset to tilemap so it will be ideally centered
        for layer in list(LevelLayer):
            self.__draw_level_layer(layer)

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
