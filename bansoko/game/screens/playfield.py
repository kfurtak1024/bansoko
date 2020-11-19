"""Module defining the main game screen."""
from dataclasses import dataclass
from typing import Optional

import pyxel

from bansoko.game.level import InputAction, Level
from bansoko.game.profile import LevelScore
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point
from bansoko.graphics.sprite import Sprite
from bansoko.gui.input import VirtualButton
from bansoko.gui.navigator import ScreenController, BaseScreenController


@dataclass(frozen=True)
class CockpitElements:
    # TODO: Rename those digits!
    digits_yellow: Sprite
    digits_blue: Sprite
    digits_red: Sprite
    rewind_icon: Sprite
    joystick_neutral: Sprite
    joystick_move: Sprite


class PlayfieldScreen(BaseScreenController):
    """Main game screen controller.

    Screen controller allowing player to "play" the level. It evaluates end-game conditions
    and switches to Level Completed screen when those are met.
    It is also possible to pause the game by pressing either 'Escape' or 'Start'
    (on a gamepad). That switches to Game Paused screen.
    """

    def __init__(self, screen_factory: ScreenFactory, level_num: int):
        bundle = screen_factory.get_bundle()
        profile = screen_factory.get_player_profile()
        super().__init__(screen=bundle.get_screen("playfield"))
        self.screen_factory = screen_factory
        self.level = Level(bundle.get_level_template(level_num))
        self.ui_elements = CockpitElements(
            digits_yellow=bundle.get_sprite("digits_yellow"),
            digits_blue=bundle.get_sprite("digits_blue"),
            digits_red=bundle.get_sprite("digits_fat_red"),
            rewind_icon=bundle.get_sprite("rewind_icon"),
            joystick_neutral=bundle.get_sprite("joystick_neutral"),
            joystick_move=bundle.get_sprite("joystick_move"))
        self.how_to_play_shown = False
        profile.last_played_level = level_num

    def update(self, dt_in_ms: float) -> ScreenController:
        if self.level.level_num == 0 and not self.how_to_play_shown:
            self.how_to_play_shown = True
            return self.screen_factory.get_how_to_play_screen()

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
        self._draw_dynamic_cockpit()
        self._draw_level_statistics()

    def _draw_level(self) -> None:
        pyxel.cls(0)
        # TODO: Should be taken from resources metadata!
        pyxel.clip(10, 20, 238, 188)
        self.level.draw()
        pyxel.clip()

    def _draw_dynamic_cockpit(self) -> None:
        if not self.level.last_input_action:
            self.ui_elements.joystick_neutral.draw(Point(20, 209))
            return

        input_action = self.level.last_input_action
        if input_action == InputAction.UNDO:
            self.ui_elements.joystick_neutral.draw(Point(20, 209))
            self.ui_elements.rewind_icon.draw(Point(21, 35))
        elif input_action.is_movement:
            self.ui_elements.joystick_move.draw(Point(20, 209), direction=input_action.direction)

    def _draw_level_statistics(self) -> None:
        score = self.level.level_score
        # TODO: Should be taken from resources metadata!
        _draw_digits(Point(40, 8), "{:>3d}".format(score.level_num), self.ui_elements.digits_yellow)
        _draw_digits(Point(174, 10), score.time, self.ui_elements.digits_red, colon_size=4)
        _draw_digits(Point(145, 227), "{:>4d}".format(score.steps), self.ui_elements.digits_yellow)
        _draw_digits(Point(145, 238), "{:>4d}".format(score.pushes), self.ui_elements.digits_blue)

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
