"""Module defining the main game screen."""
from typing import Optional

import pyxel

from bansoko.game.core import Level, InputAction
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics.background import Background
from bansoko.gui.input import InputSystem, VirtualButton
from bansoko.gui.screen import Screen


class PlayfieldScreen(Screen):
    """
    Main game screen.
    Screen allows player to "play" the level. It evaluates end-game conditions
    and switches to Level Completed screen when those are met.
    It is also possible to pause the game by pressing either 'Escape' or 'Start'
    (on a gamepad). That switches to Game Paused screen.

    Arguments:
        screen_factory - used for creation of screens this screen will navigate to
        level - level to play
        background - background to be drawn for this screen
    """

    def __init__(self, screen_factory: ScreenFactory, level: Level,
                 background: Optional[Background]):
        super().__init__(background)
        self.screen_factory = screen_factory
        self.level = level
        self.input = InputSystem()

    def activate(self) -> None:
        self.input.reset()

    def update(self) -> Screen:
        self.input.update()
        if self.input.is_button_pressed(VirtualButton.START):
            return self.screen_factory.get_game_paused_screen(self.level.statistics.level_num)

        if self.level.is_completed:
            return self.screen_factory.get_level_completed_screen(self.level.statistics)

        self.level.process_input(self.__get_input_action())
        self.level.update()

        # TODO: Just for tests!
        if pyxel.btnp(pyxel.KEY_SPACE):
            return self.screen_factory.get_level_completed_screen(self.level.statistics)

        return self

    def draw(self) -> None:
        super().draw()
        self.level.draw()
        level = self.level.statistics.level_num
        pyxel.text(7, (16 - pyxel.FONT_HEIGHT) // 2, "LEVEL " + str(level + 1), 7)
        pyxel.text(70, 255 - 24 - 2 * pyxel.FONT_HEIGHT, "<SPACE> COMPLETE LEVEL", 7)
        pyxel.text(100, 256 - 20, "TIME: ??:??\nSTEPS: ???", 7)

    def __get_input_action(self) -> Optional[InputAction]:
        if self.input.is_button_down(VirtualButton.UP):
            return InputAction.MOVE_UP
        elif self.input.is_button_down(VirtualButton.DOWN):
            return InputAction.MOVE_DOWN
        elif self.input.is_button_down(VirtualButton.LEFT):
            return InputAction.MOVE_LEFT
        elif self.input.is_button_down(VirtualButton.RIGHT):
            return InputAction.MOVE_RIGHT
        elif self.input.is_button_down(VirtualButton.ACTION):
            return InputAction.UNDO
        return None
