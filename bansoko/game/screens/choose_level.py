"""Module defining game screen for choosing a level to be played."""

import pyxel

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point, Size
from bansoko.graphics.text import draw_text, TextStyle
from bansoko.gui.menu import MenuScreen, MenuItem, Menu

LEVEL_SELECTED_STYLE = TextStyle(color=10)
LEVEL_LOCKED_STYLE = TextStyle(color=4)
LEVEL_UNLOCKED_STYLE = TextStyle(color=5)
LEVEL_COMPLETED_STYLE = TextStyle(color=3)


class LevelMenuItem(MenuItem):
    """LevelMenuItem represents a menu item used for selecting level on ChooseLevel screen."""
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
        return Size(44, 51)

    @property
    def text_style(self) -> TextStyle:
        """Text style of the menu item.

        It depends on the status of level completion the menu item is referring to.
        """
        if self.player_profile.is_level_completed(self.level_num):
            return LEVEL_COMPLETED_STYLE
        if self.player_profile.is_level_unlocked(self.level_num):
            return LEVEL_UNLOCKED_STYLE

        return LEVEL_LOCKED_STYLE

    @property
    def level_unlocked(self) -> bool:
        """Does this menu item represent already unlocked level."""
        return self.player_profile.is_level_unlocked(self.level_num)

    @property
    def level_completed(self) -> bool:
        """Does this menu item represent completed level."""
        return self.player_profile.is_level_completed(self.level_num)

    def draw(self, position: Point, selected: bool = False) -> None:
        # TODO: Under construction
        draw_text(position.offset(3, 3), f"LEVEL {self.level_num + 1}", self.text_style)

        if not self.level_unlocked:
            self.locked_icon.draw(position.offset(3, 10))
        else:
            self._draw_level_thumbnail(position.offset(3, 10))

        if self.level_completed:
            self.check_icon.draw(position.offset(3, 38))

        if selected:
            self._draw_level_score(Point(13, 236))

        self._draw_frame(position, selected)

    def _draw_level_thumbnail(self, position: Point) -> None:
        # pyxel.rect(position.x, position.y, 32, 32, 1)
        # TODO: Hard coded image bank (2)
        pyxel.blt(position.x, position.y, 2, 32 * (self.level_num % 8), 32 * (self.level_num // 8),
                  32, 32, colkey=0)

    def _draw_level_score(self, position: Point) -> None:
        level_score = self.player_profile.levels_scores[self.level_num]
        pyxel.line(position.x, position.y, position.x + 213, position.y, LEVEL_SELECTED_STYLE.color)

        if self.level_completed:
            text = f"TIME: {level_score.time} "\
                   f"PUSHES: {level_score.pushes} "\
                   f"STEPS: {level_score.steps}"
        elif self.level_unlocked:
            text = "LEVEL NOT COMPLETED"
        else:
            text = "LEVEL LOCKED"

        draw_text(position.offset(0, 4), text, LEVEL_SELECTED_STYLE)

    def _draw_frame(self, position: Point, selected: bool) -> None:
        style = LEVEL_SELECTED_STYLE if selected else self.text_style
        pyxel.rectb(position.x, position.y, 38, 45, style.color)


class ChooseLevelScreen(MenuScreen):
    """Screen allowing player to choose a level to play.

    Player can choose a level from all unlocked levels (Level is "unlocked"
    when its predecessor level is completed)
    From this screen it is also possible to navigate back to Main Menu.
    """

    def __init__(self, screen_factory: ScreenFactory):
        bundle = screen_factory.get_bundle()
        menu = Menu.with_defaults(
            tuple([
                LevelMenuItem(level_num, screen_factory) for level_num in range(bundle.num_levels)
            ]),
            columns=5, rows=4, position=Point(13, 30))
        super().__init__(
            menu=menu,
            allow_going_back=True,
            background=bundle.get_background("choose_level"))
        self.scroll_to_item(screen_factory.get_player_profile().last_played_level)

    def draw(self, draw_as_secondary: bool = False) -> None:
        super().draw(draw_as_secondary)
        self._draw_scroll_bar()
        pyxel.text(8, 8, "CHOOSE LEVEL", 7)

    def _draw_scroll_bar(self) -> None:
        # TODO: Hard-coded scroll bar (for now!)
        scrollbar_size_in_pixels = round(super().scrollbar_size * 199)
        scrollbar_position_in_pixels = round(super().scrollbar_position * 199)
        pyxel.rectb(235, 30, 8, 199 + 2, 5)
        pyxel.rect(236, 31 + scrollbar_position_in_pixels, 6, scrollbar_size_in_pixels, 5)
