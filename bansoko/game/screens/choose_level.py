"""Module defining screen controller for choosing a level to be played."""

import pyxel

from bansoko import LEVEL_THUMBNAIL_IMAGE_BANK, LEVEL_WIDTH, LEVEL_HEIGHT
from bansoko.game.screens.gui_consts import GuiPosition, GuiColor, GuiSprite
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point, Size
from bansoko.graphics.sprite import Sprite
from bansoko.graphics.text import draw_text, TextStyle
from bansoko.gui.menu import MenuController, MenuItem, Menu, MenuLayout


class LevelMenuItem(MenuItem):
    """LevelMenuItem represents a menu item used for selecting level on ChooseLevel screen."""

    def __init__(self, level_num: int, screen_factory: ScreenFactory):
        super().__init__(lambda: screen_factory.get_playfield_screen(level_num))
        self.level_num = level_num
        self.player_profile = screen_factory.get_player_profile()
        self.gui_consts = screen_factory.get_bundle().get_gui_consts()

    @property
    def disabled(self) -> bool:
        return self.level_num > self.player_profile.last_unlocked_level

    @property
    def size(self) -> Size:
        pos = self._get_position(GuiPosition.LEVEL_ITEM_SIZE)
        return Size(pos.x, pos.y)

    @property
    def text_style(self) -> TextStyle:
        """Text style of the menu item.

        It depends on the status of level completion the menu item is referring to.
        """
        if self.player_profile.is_level_completed(self.level_num):
            return self._get_text_style(GuiColor.LEVEL_COMPLETED_COLOR)
        if self.player_profile.is_level_unlocked(self.level_num):
            return self._get_text_style(GuiColor.LEVEL_UNLOCKED_COLOR)

        return self._get_text_style(GuiColor.LEVEL_LOCKED_COLOR)

    @property
    def level_unlocked(self) -> bool:
        """Does this menu item represent already unlocked level."""
        return self.player_profile.is_level_unlocked(self.level_num)

    @property
    def level_completed(self) -> bool:
        """Does this menu item represent completed level."""
        return self.player_profile.is_level_completed(self.level_num)

    def draw(self, position: Point, selected: bool = False) -> None:
        draw_text(position.offset(self._get_position(GuiPosition.LEVEL_ITEM_TITLE_POS)),
                  f"LEVEL {self.level_num}", self.text_style)

        if not self.level_unlocked:
            self._get_sprite(GuiSprite.LOCKED_ICON).draw(position.offset(
                self._get_position(GuiPosition.LEVEL_LOCKED_ICON_POS)))
        else:
            self._draw_level_thumbnail(position.offset(
                self._get_position(GuiPosition.LEVEL_THUMBNAIL_POS)))

        if self.level_completed:
            self._get_sprite(GuiSprite.CHECKED_ICON).draw(position.offset(
                self._get_position(GuiPosition.LEVEL_COMPLETED_ICON_POS)))

        if selected:
            self._draw_level_score(self._get_position(GuiPosition.LEVEL_SCORE_POS))

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

        draw_text(position, text, self._get_text_style(GuiColor.LEVEL_SELECTED_COLOR))

    def _draw_frame(self, position: Point, selected: bool) -> None:
        level_item_size = self._get_position(GuiPosition.LEVEL_ITEM_SIZE)
        style = self._get_text_style(GuiColor.LEVEL_SELECTED_COLOR) if selected else self.text_style
        pyxel.rectb(position.x, position.y, level_item_size.x, level_item_size.y, style.color)

    def _get_sprite(self, gui_sprite: GuiSprite) -> Sprite:
        return self.gui_consts.get_sprite(gui_sprite)

    def _get_position(self, gui_position: GuiPosition) -> Point:
        return self.gui_consts.get_position(gui_position)

    def _get_text_style(self, color: GuiColor) -> TextStyle:
        return TextStyle(self.gui_consts.get_color(color))


class ChooseLevelController(MenuController):
    """Screen controller allowing player to choose a level to play.

    Player can choose a level from all unlocked levels (Level is "unlocked"
    when its predecessor level is completed)
    From this screen it is also possible to navigate back to Main Menu.
    """

    def __init__(self, screen_factory: ScreenFactory):
        bundle = screen_factory.get_bundle()
        screen = bundle.get_screen("choose_level")
        item_space = bundle.get_gui_consts().get_position(GuiPosition.LEVEL_ITEM_SPACE)
        menu = Menu.with_defaults(tuple([
            LevelMenuItem(level_num, screen_factory) for level_num in range(bundle.num_levels)
        ]), MenuLayout(columns=5, rows=4, position=screen.menu_position,
                       item_space=Size(item_space.x, item_space.y)))
        super().__init__(menu=menu, allow_going_back=True, screen=screen)
        self.select_and_scroll_to_item(screen_factory.get_player_profile().last_played_level)
        self.level_selected_color = bundle.get_gui_consts().get_color(GuiColor.LEVEL_SELECTED_COLOR)

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
                   scrollbar_rect.w, scrollbar_size_in_pixels, self.level_selected_color)
