"""
Module exposing the main game screen.
"""
import pyxel

from .screen_factory import ScreenFactory
from ..level import Direction, Level
from ...gui.input import InputSystem, VirtualButton
from ...gui.screen import Screen


class GameScreen(Screen):
    """
    Main game screen.
    Screen allows player to "play" the level. It evaluates end-game conditions
    and switches to Level Completed screen when those are met.
    It is also possible to pause the game by pressing either 'Escape' or 'Start'
    (on a gamepad). That switches to Game Paused screen.

    Arguments:
        screen_factory - used for creation of screens this screen will navigate to
        level - level to play
    """

    def __init__(self, screen_factory: ScreenFactory, level: Level):
        self.screen_factory = screen_factory
        self.level = level
        self.input = InputSystem()

    def activate(self) -> None:
        self.input.reset()

    def update(self) -> Screen:
        self.input.update()
        if self.input.is_button_pressed(VirtualButton.START):
            return self.screen_factory.get_game_paused_screen(self.level.statistics.level_num)

        if self.level.is_completed():
            return self.screen_factory.get_level_completed_screen(self.level.statistics)

        if self.input.is_button_pressed(VirtualButton.UP):
            self.level.move_player(Direction.UP)
        elif self.input.is_button_pressed(VirtualButton.DOWN):
            self.level.move_player(Direction.DOWN)
        elif self.input.is_button_pressed(VirtualButton.LEFT):
            self.level.move_player(Direction.LEFT)
        elif self.input.is_button_pressed(VirtualButton.RIGHT):
            self.level.move_player(Direction.RIGHT)

        self.level.update()

        # TODO: Just for tests!
        if pyxel.btnp(pyxel.KEY_SPACE):
            return self.screen_factory.get_level_completed_screen(self.level.statistics)

        return self

    def draw(self) -> None:
        self.level.draw()
        level = self.level.statistics.level_num
        pyxel.rectb(0, 0, 256, 15, 3)
        pyxel.text(7, (16 - pyxel.FONT_HEIGHT) // 2, "LEVEL " + str(level + 1), 7)
        pyxel.text(70, 255 - 24 - 2 * pyxel.FONT_HEIGHT, "<SPACE> COMPLETE LEVEL", 7)
