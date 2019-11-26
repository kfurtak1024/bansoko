"""
Module exposing the main game screen.
"""
import pyxel

from .screen_factory import ScreenFactory
from ..level import LevelStatistics, LEVEL_SIZE, TILE_SIZE
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
    """

    def __init__(self, screen_factory: ScreenFactory, level: int):
        self.level_stats = LevelStatistics(level)
        self.screen_factory = screen_factory
        self.input = InputSystem()

    def activate(self) -> None:
        self.input.reset()

    def update(self) -> Screen:
        self.input.update()
        if self.input.is_button_pressed(VirtualButton.START):
            return self.screen_factory.get_game_paused_screen(self.level_stats.level)

        if pyxel.btnp(pyxel.KEY_SPACE):
            return self.screen_factory.get_level_completed_screen(self.level_stats)
        return self

    def draw(self) -> None:
        level = self.level_stats.level
        tilemap_u = LEVEL_SIZE * (level % TILE_SIZE)
        tilemap_v = LEVEL_SIZE * (level // TILE_SIZE)
        pyxel.bltm(0, 0, 0, tilemap_u, tilemap_v, LEVEL_SIZE, LEVEL_SIZE)
        pyxel.rectb(0, 0, 256, 15, 3)
        pyxel.text(7, (16 - pyxel.FONT_HEIGHT) // 2, "LEVEL " + str(level + 1), 7)
        pyxel.text(70, 255 - 24 - 2 * pyxel.FONT_HEIGHT, "<SPACE> COMPLETE LEVEL", 7)
