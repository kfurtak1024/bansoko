"""Module defining game screen for choosing a level to be played."""

import pyxel

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point, Size
from bansoko.graphics.text import draw_text
from bansoko.gui.menu import MenuScreen, MenuItem, MenuConfig

LEVEL_LOCKED_BASE_COLOR = 4
LEVEL_UNLOCKED_BASE_COLOR = 5
LEVEL_COMPLETED_BASE_COLOR = 3


class LevelMenuItem(MenuItem):
    def __init__(self, level_num: int, screen_factory: ScreenFactory):
        super().__init__(lambda: screen_factory.get_playfield_screen(level_num))
        self.level_num = level_num
        self.player_profile = screen_factory.get_player_profile()
        self.check_icon = screen_factory.get_bundle().get_sprite("check_icon")
        self.locked_icon = screen_factory.get_bundle().get_sprite("locked_icon")

    @property
    def disabled(self) -> bool:
        return self.level_num > self.player_profile.last_unlocked_level

    @property
    def size(self) -> Size:
        return Size(74, 52)

    @property
    def base_color(self) -> int:
        if self.player_profile.is_level_completed(self.level_num):
            return LEVEL_COMPLETED_BASE_COLOR
        if self.player_profile.is_level_unlocked(self.level_num):
            return LEVEL_UNLOCKED_BASE_COLOR

        return LEVEL_LOCKED_BASE_COLOR

    def draw(self, position: Point, selected: bool = False) -> None:
        # TODO: Under construction
        draw_text(position.offset(3, 3), f"#{self.base_color}LEVEL " + str(self.level_num + 1))

        if not self.player_profile.is_level_unlocked(self.level_num):
            self.locked_icon.draw(position.offset(18, 10))
        else:
            self._draw_level_thumbnail(position.offset(3, 10))

        if self.player_profile.is_level_completed(self.level_num):
            self._draw_level_score(position.offset(38, 7))
            self.check_icon.draw(position.offset(3, 38))

        self._draw_frame(position, selected)

    def _draw_level_thumbnail(self, position: Point) -> None:
        pyxel.blt(position.x, position.y, 2, 32 * (self.level_num % 8), 32 * (self.level_num // 8),
                  32, 32)

    def _draw_level_score(self, position: Point) -> None:
        level_score = self.player_profile.levels_scores[self.level_num]
        draw_text(position,
                  f"#DTIME:\n#3{level_score.time}\n"
                  f"#DPUSHES:\n#3{level_score.pushes}\n"
                  f"#DSTEPS:\n#3{level_score.steps}")

    def _draw_frame(self, position: Point, selected: bool) -> None:
        if selected:
            pyxel.rectb(position.x, position.y, 67, 45, 10)
        else:
            pyxel.rectb(position.x, position.y, 67, 45, self.base_color)


class ChooseLevelScreen(MenuScreen):
    """Screen allowing player to choose a level to play.

    Player can choose a level from all unlocked levels (Level is "unlocked"
    when its predecessor level is completed)
    From this screen it is also possible to navigate back to Main Menu.
    """

    def __init__(self, screen_factory: ScreenFactory):
        bundle = screen_factory.get_bundle()
        super().__init__(
            tuple([
                LevelMenuItem(level_num, screen_factory) for level_num in range(bundle.num_levels)
            ]),
            MenuConfig(columns=3, rows=4, allow_going_back=True,
                       background=bundle.get_background("choose_level")),
            position=Point(13, 30))

    def draw(self) -> None:
        super().draw()
        # TODO: Hard-coded scroll bar (for now!)
        scrollbar_size_in_pixels = int(super().scrollbar_size * 199)
        scrollbar_position_in_pixels = int(super().scrollbar_position * 199)
        pyxel.rectb(235, 30, 8, 199 + 2, 5)
        pyxel.rect(236, 31 + scrollbar_position_in_pixels, 6, scrollbar_size_in_pixels, 5)
        pyxel.text(8, 8, "CHOOSE LEVEL", 7)
