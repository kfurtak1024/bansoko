"""Module defining game screen for choosing a level to be played."""

import pyxel

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point, Size
from bansoko.gui.menu import MenuScreen, MenuItem, MenuConfig


# TODO: Add horizontal and vertical space
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
            self._draw_level_score()

    def _draw_level_score(self) -> None:
        text = ""
        if not self.player_profile.is_level_unlocked(self.level_num):
            text = "LOCKED"
        elif not self.player_profile.is_level_completed(self.level_num):
            text = "NOT COMPLETED"
        else:
            level_score = self.player_profile.levels_scores[self.level_num]
            if level_score:
                text = f"TIME:   {level_score.time}\n" \
                       f"PUSHES: {level_score.pushes}\n" \
                       f"MOVES:  {level_score.steps}"

        pyxel.text(8, 220, f"LEVEL STATS ({self.level_num}):\n============\n{text}", 10)


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
            MenuConfig(columns=6, rows=5, allow_going_back=True,
                       background=bundle.get_background("choose_level")))

    def draw(self) -> None:
        super().draw()
        # TODO: Hard-coded scroll bar (for now!)
        scrollbar_size_in_pixels = int(super().scrollbar_size * 186)
        scrollbar_position_in_pixels = int(super().scrollbar_position * 186)
        pyxel.rectb(244, 30, 8, 186 + 2, 7)
        pyxel.rect(245, 31 + scrollbar_position_in_pixels, 6, scrollbar_size_in_pixels, 8)
        pyxel.text(8, 8, "CHOOSE LEVEL", 7)
