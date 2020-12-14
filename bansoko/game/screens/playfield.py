"""Module defining the main game screen."""
from typing import Optional

import pyxel

from bansoko.game.level import InputAction, Level
from bansoko.game.screens.gui_consts import GuiSprite, GuiPosition
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point, Direction
from bansoko.graphics.animation import AnimationPlayer, Animation
from bansoko.graphics.sprite import Sprite
from bansoko.gui.input import VirtualButton
from bansoko.gui.navigator import ScreenController, BaseScreenController

PRINTING_RECEIPT_ANIMATION_FRAME_TIME = 120


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
        self.gui_consts = screen_factory.get_bundle().get_gui_consts()
        self.printing_animation = Animation(bundle.get_sprite("printing_receipt"),
                                            PRINTING_RECEIPT_ANIMATION_FRAME_TIME)
        self.level_completed_animation_player: Optional[AnimationPlayer] = None
        self.how_to_play_shown = not show_how_to_play
        profile.last_played_level = level_num

    def update(self, dt_in_ms: float) -> ScreenController:
        if not self.how_to_play_shown:
            self.how_to_play_shown = True
            return self.screen_factory.get_how_to_play_screen()

        super().update(dt_in_ms)

        if self.level_completed_animation_player:
            return self._update_level_completed_player(dt_in_ms)

        if self.input.is_button_pressed(VirtualButton.START):
            return self.screen_factory.get_game_paused_screen(self.level.level_num)

        if self.level.is_completed:
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
        if self.level_completed_animation_player:
            self.level_completed_animation_player.draw(
                self._get_position(GuiPosition.COCKPIT_RECEIPT_POS))

    def _draw_dynamic_cockpit(self) -> None:
        if not self.level.last_input_action:
            self._draw_sprite(GuiSprite.JOYSTICK_NEUTRAL, GuiPosition.COCKPIT_JOYSTICK_POS)
            self._draw_sprite(GuiSprite.REWIND_BUTTON, GuiPosition.COCKPIT_REWIND_BUTTON_POS,
                              frame=0)
            self._draw_sprite(GuiSprite.LEFT_HAND, GuiPosition.LEFT_HAND_NEUTRAL_POS)
            return

        input_action = self.level.last_input_action
        if input_action == InputAction.UNDO:
            self._draw_sprite(GuiSprite.JOYSTICK_NEUTRAL, GuiPosition.COCKPIT_JOYSTICK_POS)
            self._draw_sprite(GuiSprite.REWIND_ICON, GuiPosition.COCKPIT_REWIND_ICON_POS)
            self._draw_sprite(GuiSprite.REWIND_BUTTON, GuiPosition.COCKPIT_REWIND_BUTTON_POS,
                              frame=1)
            self._draw_sprite(GuiSprite.LEFT_HAND_PRESSING_BUTTON,
                              GuiPosition.LEFT_HAND_PRESSING_BUTTON_POS)
        elif input_action.is_movement:
            self._draw_sprite(GuiSprite.JOYSTICK_MOVE, GuiPosition.COCKPIT_JOYSTICK_POS,
                              direction=input_action.direction)
            if input_action.direction == Direction.LEFT:
                self._draw_sprite(GuiSprite.LEFT_HAND, GuiPosition.LEFT_HAND_LEFT_POS)
            elif input_action.direction == Direction.RIGHT:
                self._draw_sprite(GuiSprite.LEFT_HAND, GuiPosition.LEFT_HAND_RIGHT_POS)
            elif input_action.direction == Direction.UP:
                self._draw_sprite(GuiSprite.LEFT_HAND, GuiPosition.LEFT_HAND_UP_POS)
            elif input_action.direction == Direction.DOWN:
                self._draw_sprite(GuiSprite.LEFT_HAND, GuiPosition.LEFT_HAND_DOWN_POS)
            self._draw_sprite(GuiSprite.REWIND_BUTTON, GuiPosition.COCKPIT_REWIND_BUTTON_POS,
                              frame=0)

    def _draw_level_statistics(self) -> None:
        score = self.level.level_score
        self._draw_digits(GuiPosition.COCKPIT_LEVEL_NUM_POS, "{:>3d}".format(score.level_num),
                          GuiSprite.LEVEL_DIGITS)
        self._draw_digits(GuiPosition.COCKPIT_LEVEL_TIME_POS, score.time, GuiSprite.TIME_DIGITS,
                          colon_size=4)
        self._draw_digits(GuiPosition.COCKPIT_LEVEL_STEPS_POS, "{:>4d}".format(score.steps),
                          GuiSprite.STEPS_DIGITS)
        self._draw_digits(GuiPosition.COCKPIT_LEVEL_PUSHES_POS, "{:>4d}".format(score.pushes),
                          GuiSprite.PUSHES_DIGITS)

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
        self.level_completed_animation_player = AnimationPlayer(self.printing_animation)
        return self

    def _update_level_completed_player(self, dt_in_ms: float) -> ScreenController:
        if self.level_completed_animation_player:
            if self.level_completed_animation_player.stopped:
                return self.screen_factory.get_level_completed_screen(self.level.level_score)
            self.level_completed_animation_player.update(dt_in_ms)
        return self

    def _get_position(self, gui_position: GuiPosition) -> Point:
        return self.gui_consts.get_position(gui_position)

    def _get_sprite(self, gui_sprite: GuiSprite) -> Sprite:
        return self.gui_consts.get_sprite(gui_sprite)

    def _draw_sprite(self, gui_sprite: GuiSprite, gui_position: GuiPosition,
                     frame: int = 0, direction: Direction = Direction.UP) -> None:
        self._get_sprite(gui_sprite).draw(self._get_position(gui_position), frame=frame,
                                          direction=direction)

    def _draw_digits(self, gui_position: GuiPosition, text: str, gui_sprite: GuiSprite,
                     colon_size: Optional[int] = None) -> None:
        position = self._get_position(gui_position)
        sprite = self._get_sprite(gui_sprite)
        char_pos = position
        for char in text:
            if char.isdigit():
                sprite.draw(position=char_pos, frame=int(char))
            char_size = colon_size if (char == ":" and colon_size) else sprite.width
            char_pos = char_pos.offset(Point(char_size + 1, 0))
