"""Module defining game screen for choosing a level to be played."""
from typing import Optional

import pyxel

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point, Size
from bansoko.gui.menu import MenuScreen, MenuItem
from gui.screen import Screen


class LevelMenuItem(MenuItem):
    def __init__(self, level_num: int, screen_factory: ScreenFactory):
        self.level_num = level_num
        self.player_profile = screen_factory.get_player_profile()
        self.screen_to_switch_to = lambda: screen_factory.get_playfield_screen(level_num)
        self.check_icon = screen_factory.get_bundle().get_sprite("check_icon")
        self.locked_icon = screen_factory.get_bundle().get_sprite("locked_icon")

    @property
    def disabled(self) -> bool:
        return self.level_num > self.player_profile.last_unlocked_level

    @property
    def size(self) -> Size:
        # TODO: Under construction
        return Size(39, 39)

    def draw(self, position: Point, selected: bool = False) -> None:
        # TODO: Under construction
        if self.disabled:
            self.locked_icon.draw(position)
        else:
            pyxel.blt(position.x, position.y, 2, 32 * (self.level_num % 8),
                      32 * (self.level_num // 8), 32, 32)
        if selected:
            pyxel.rectb(position.x, position.y, 32, 32, 10)
        else:
            if not self.player_profile.is_level_unlocked(self.level_num):
                pyxel.rectb(position.x, position.y, 32, 32, 4)
            elif self.player_profile.is_level_completed(self.level_num):
                pyxel.rectb(position.x, position.y, 32, 32, 3)
            else:
                pyxel.rectb(position.x, position.y, 32, 32, 5)

        pyxel.line(position.x + 1, position.y + 32, position.x + 32, position.y + 32, 1)
        pyxel.line(position.x + 32, position.y + 1, position.x + 32, position.y + 32, 1)

        if self.player_profile.is_level_completed(self.level_num):
            self.check_icon.draw(Point(position.x+32-7, position.y+32-7))

        if selected:
            text = ""
            if not self.player_profile.is_level_unlocked(self.level_num):
                text = "LOCKED"
            elif not self.player_profile.is_level_completed(self.level_num):
                text = "NOT COMPLETED"
            else:
                level_stats = self.player_profile.levels_stats[self.level_num]
                if level_stats:
                    text = level_stats.debug_description

            pyxel.text(8, 220, f"LEVEL STATS ({self.level_num}):\n============\n{text}", 10)

    def perform_action(self) -> Optional[Screen]:
        return self.screen_to_switch_to()


class ChooseLevelScreen(MenuScreen):
    """Screen allowing player to choose a level to play.

    Player can choose a level from all unlocked levels (Level is "unlocked"
    when its predecessor level is completed)
    From this screen it is also possible to navigate back to Main Menu.
    """

    def __init__(self, screen_factory: ScreenFactory):
        bundle = screen_factory.get_bundle()
        super().__init__([
            LevelMenuItem(level_num, screen_factory) for level_num in range(bundle.num_levels)
        ], columns=6, rows=5, allow_going_back=True, background=bundle.get_background("choose_level"))

    def draw(self) -> None:
        super().draw()
        pyxel.text(8, 8, "CHOOSE LEVEL", 7)
