"""Module defining the main game screen."""
from typing import Optional

import pyxel

from bansoko.game.level import InputAction, Level
from bansoko.game.profile import LevelScore
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point
from bansoko.graphics.sprite import Sprite
from bansoko.gui.input import VirtualButton
from bansoko.gui.screen import Screen, BaseScreen


class PlayfieldScreen(BaseScreen):
    """Main game screen.

    Screen allows player to "play" the level. It evaluates end-game conditions
    and switches to Level Completed screen when those are met.
    It is also possible to pause the game by pressing either 'Escape' or 'Start'
    (on a gamepad). That switches to Game Paused screen.
    """

    def __init__(self, screen_factory: ScreenFactory, level_num: int):
        bundle = screen_factory.get_bundle()
        profile = screen_factory.get_player_profile()
        super().__init__(background=bundle.get_background("playfield"))
        self.screen_factory = screen_factory
        self.level = Level(bundle.get_level_template(level_num))
        self.digits_yellow = bundle.get_sprite("digits_yellow")
        self.digits_blue = bundle.get_sprite("digits_blue")
        self.digits_red = bundle.get_sprite("digits_fat_red")
        profile.last_played_level = level_num

    def update(self, dt_in_ms: float) -> Screen:
        super().update(dt_in_ms)

        if self.input.is_button_pressed(VirtualButton.START):
            return self.screen_factory.get_game_paused_screen(self.level.level_num)

        if self.level.is_completed:
            return self.screen_factory.get_level_completed_screen(self.level.level_score)

        self.level.process_input(self._get_input_action())
        self.level.update(dt_in_ms)

        # TODO: Just for tests! REMOVE IT IN FINAL VERSION !!!!!!!!!!!!!!!!
        if pyxel.btnp(pyxel.KEY_SPACE):
            return self.screen_factory.get_level_completed_screen(
                LevelScore(self.level.level_num, completed=True, pushes=100, steps=100,
                           time_in_ms=1000))

        return self

    def draw(self, draw_as_secondary: bool = False) -> None:
        if draw_as_secondary:
            pyxel.cls(0)
        else:
            self._draw_level()

        super().draw(draw_as_secondary)
        self._draw_level_statistics()

    def _draw_level(self) -> None:
        pyxel.cls(0)
        # TODO: Should be taken from resources metadata!
        pyxel.clip(10, 20, 238, 188)
        self.level.draw()
        pyxel.clip()

    def _draw_level_statistics(self) -> None:
        score = self.level.level_score
        _draw_digits(Point(40, 8), "{:>3d}".format(score.level_num), self.digits_yellow)
        _draw_digits(Point(174, 10), score.time, self.digits_red, colon_size=4)
        _draw_digits(Point(145, 227), "{:>4d}".format(score.steps), self.digits_yellow)
        _draw_digits(Point(145, 238), "{:>4d}".format(score.pushes), self.digits_blue)

    def _get_input_action(self) -> Optional[InputAction]:
        if self.input.is_button_down(VirtualButton.UP):
            return InputAction.MOVE_UP
        if self.input.is_button_down(VirtualButton.DOWN):
            return InputAction.MOVE_DOWN
        if self.input.is_button_down(VirtualButton.LEFT):
            return InputAction.MOVE_LEFT
        if self.input.is_button_down(VirtualButton.RIGHT):
            return InputAction.MOVE_RIGHT
        if self.input.is_button_down(VirtualButton.ACTION):
            return InputAction.UNDO
        return None


def _draw_digits(position: Point, text: str, sprite: Sprite, space: int = 1,
                 colon_size: Optional[int] = None) -> None:
    char_pos = position
    for char in text:
        if char.isdigit():
            sprite.draw(position=char_pos, frame=int(char))
        char_size = colon_size if (char == ":" and colon_size) else sprite.width
        char_pos = char_pos.offset(char_size + space, 0)
