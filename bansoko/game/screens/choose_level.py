"""Module defining screen controller for choosing a level to be played."""

import pyxel

from bansoko import LEVEL_THUMBNAIL_IMAGE_BANK, LEVEL_WIDTH, LEVEL_HEIGHT
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point, Size
from bansoko.graphics.text import draw_text, TextStyle
from bansoko.gui.menu import MenuController, MenuItem, Menu, MenuLayout

LEVEL_SELECTED_STYLE = TextStyle(color=10)
LEVEL_LOCKED_STYLE = TextStyle(color=1)
LEVEL_UNLOCKED_STYLE = TextStyle(color=5)
LEVEL_COMPLETED_STYLE = TextStyle(color=3)

LEVEL_ITEM_SIZE = Size(38, 45)
LEVEL_ITEM_SPACE = Size(6, 6)
LEVEL_ITEM_TITLE_POS = Point(3, 3)
LEVEL_LOCKED_ICON_POS = Point(3, 10)
LEVEL_COMPLETED_ICON_POS = Point(3, 38)
LEVEL_THUMBNAIL_POS = Point(3, 10)
LEVEL_SCORE_POS = Point(14, 237)


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
        return LEVEL_ITEM_SIZE

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
        draw_text(position.offset(LEVEL_ITEM_TITLE_POS), f"LEVEL {self.level_num}", self.text_style)

        if not self.level_unlocked:
            self.locked_icon.draw(position.offset(LEVEL_LOCKED_ICON_POS))
        else:
            self._draw_level_thumbnail(position.offset(LEVEL_THUMBNAIL_POS))

        if self.level_completed:
            self.check_icon.draw(position.offset(LEVEL_COMPLETED_ICON_POS))

        if selected:
            self._draw_level_score(LEVEL_SCORE_POS)

        self._draw_frame(position, selected)

    def _draw_level_thumbnail(self, position: Point) -> None:
        pyxel.blt(position.x, position.y, LEVEL_THUMBNAIL_IMAGE_BANK,
                  LEVEL_WIDTH * (self.level_num % 8),
                  LEVEL_HEIGHT * (self.level_num // 8),
                  LEVEL_WIDTH, LEVEL_HEIGHT, colkey=0)

    def _draw_level_score(self, position: Point) -> None:
        level_score = self.player_profile.levels_scores[self.level_num]

        if self.level_completed:
            text = f"TIME: {level_score.time}  " \
                   f"PUSHES: {level_score.pushes: >4}  " \
                   f"STEPS: {level_score.steps: >4}"
        else:
            text = "LEVEL NOT COMPLETED" if self.level_unlocked else "LEVEL LOCKED"

        draw_text(position, text, LEVEL_SELECTED_STYLE)

    def _draw_frame(self, position: Point, selected: bool) -> None:
        style = LEVEL_SELECTED_STYLE if selected else self.text_style
        pyxel.rectb(position.x, position.y, LEVEL_ITEM_SIZE.width, LEVEL_ITEM_SIZE.height,
                    style.color)


class ChooseLevelController(MenuController):
    """Screen controller allowing player to choose a level to play.

    Player can choose a level from all unlocked levels (Level is "unlocked"
    when its predecessor level is completed)
    From this screen it is also possible to navigate back to Main Menu.
    """

    def __init__(self, screen_factory: ScreenFactory):
        bundle = screen_factory.get_bundle()
        screen = bundle.get_screen("choose_level")
        menu = Menu.with_defaults(tuple([
            LevelMenuItem(level_num, screen_factory) for level_num in range(bundle.num_levels)
        ]), MenuLayout(columns=5, rows=4, position=screen.menu_position,
                       item_space=LEVEL_ITEM_SPACE))
        super().__init__(menu=menu, allow_going_back=True, screen=screen)
        self.select_and_scroll_to_item(screen_factory.get_player_profile().last_played_level)

    def draw(self, draw_as_secondary: bool = False) -> None:
        super().draw(draw_as_secondary)
        self._draw_scroll_bar()

    def _draw_scroll_bar(self) -> None:
        if not self.screen or not self.screen.menu_scrollbar_rect:
            return

        scrollbar_rect = self.screen.menu_scrollbar_rect
        scrollbar_size_in_pixels = round(super().scrollbar_size * scrollbar_rect.h)
        scrollbar_position_in_pixels = round(super().scrollbar_position * scrollbar_rect.h)
        pyxel.rect(scrollbar_rect.x, scrollbar_rect.y + scrollbar_position_in_pixels,
                   scrollbar_rect.w, scrollbar_size_in_pixels, LEVEL_SELECTED_STYLE.color)
