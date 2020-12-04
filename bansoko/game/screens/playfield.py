"""Module defining the main game screen."""
from dataclasses import dataclass
from typing import Optional

import pyxel

from bansoko.game.level import InputAction, Level
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point
from bansoko.graphics.animation import AnimationPlayer, Animation
from bansoko.graphics.sprite import Sprite
from bansoko.gui.input import VirtualButton
from bansoko.gui.navigator import ScreenController, BaseScreenController


@dataclass(frozen=True)
class CockpitElements:
    """Collection of dynamic elements of cockpit."""
    digits_level: Sprite
    digits_steps: Sprite
    digits_pushes: Sprite
    digits_time: Sprite
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

    def __init__(self, screen_factory: ScreenFactory, level_num: int,
                 show_how_to_play: bool = False):
        bundle = screen_factory.get_bundle()
        profile = screen_factory.get_player_profile()
        super().__init__(screen=bundle.get_screen("playfield"))
        self.screen_factory = screen_factory
        self.level = Level(bundle.get_level_template(level_num))
        self.ui_elements = CockpitElements(
            digits_level=bundle.get_sprite("digits_yellow"),
            digits_steps=bundle.get_sprite("digits_yellow"),
            digits_pushes=bundle.get_sprite("digits_blue"),
            digits_time=bundle.get_sprite("digits_fat_red"),
            rewind_icon=bundle.get_sprite("rewind_icon"),
            joystick_neutral=bundle.get_sprite("joystick_neutral"),
            joystick_move=bundle.get_sprite("joystick_move"))
        self.printing_animation = Animation(bundle.get_sprite("printing_receipt"), 120)
        self.level_completed_player: Optional[AnimationPlayer] = None
        self.how_to_play_shown = not show_how_to_play
        profile.last_played_level = level_num

    def update(self, dt_in_ms: float) -> ScreenController:
        if not self.how_to_play_shown:
            self.how_to_play_shown = True
            return self.screen_factory.get_how_to_play_screen()

        super().update(dt_in_ms)

        if self.level_completed_player:
            return self._update_level_completed_player(dt_in_ms)

        if self.input.is_button_pressed(VirtualButton.START):
            return self.screen_factory.get_game_paused_screen(self.level.level_num)

        # TODO: Just for tests! REMOVE SKIPPING LEVEL WITH SPACE IT IN FINAL VERSION !!!!!!!!!!!!!!
        if self.level.is_completed or pyxel.btnp(pyxel.KEY_SPACE):
            return self._start_level_completed_player()

        self.level.process_input(self._get_input_action())
        self.level.update(dt_in_ms)

        return self

    def draw(self, draw_as_secondary: bool = False) -> None:
        pyxel.cls(0)
        if not draw_as_secondary:
            self.level.draw()

        super().draw(draw_as_secondary)
        self._draw_dynamic_cockpit()
        self._draw_level_statistics()
        if self.level_completed_player:
            self.level_completed_player.draw(Point(202, 202))

    def _draw_dynamic_cockpit(self) -> None:
        if not self.level.last_input_action:
            self.ui_elements.joystick_neutral.draw(Point(18, 209))
            return

        input_action = self.level.last_input_action
        if input_action == InputAction.UNDO:
            self.ui_elements.joystick_neutral.draw(Point(18, 209))
            self.ui_elements.rewind_icon.draw(Point(21, 35))
        elif input_action.is_movement:
            self.ui_elements.joystick_move.draw(Point(18, 209), direction=input_action.direction)

    def _draw_level_statistics(self) -> None:
        score = self.level.level_score
        # TODO: Should be taken from resources metadata!
        _draw_digits(Point(40, 8), "{:>3d}".format(score.level_num), self.ui_elements.digits_level)
        _draw_digits(Point(174, 10), score.time, self.ui_elements.digits_time, colon_size=4)
        _draw_digits(Point(145, 227), "{:>4d}".format(score.steps), self.ui_elements.digits_steps)
        _draw_digits(Point(145, 238), "{:>4d}".format(score.pushes), self.ui_elements.digits_pushes)

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

    def _start_level_completed_player(self) -> ScreenController:
        self.level_completed_player = AnimationPlayer(self.printing_animation)
        return self

    def _update_level_completed_player(self, dt_in_ms: float) -> ScreenController:
        if self.level_completed_player.stopped:
            return self.screen_factory.get_level_completed_screen(self.level.level_score)
        self.level_completed_player.update(dt_in_ms)
        return self


def _draw_digits(position: Point, text: str, sprite: Sprite, space: int = 1,
                 colon_size: Optional[int] = None) -> None:
    char_pos = position
    for char in text:
        if char.isdigit():
            sprite.draw(position=char_pos, frame=int(char))
        char_size = colon_size if (char == ":" and colon_size) else sprite.width
        char_pos = char_pos.offset(char_size + space, 0)
