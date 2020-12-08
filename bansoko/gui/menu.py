"""Module for game menus management."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import reduce
from itertools import islice
from typing import Callable, Optional, Iterable, Tuple

from bansoko.graphics import Size, Point, max_size, center_in_rect
from bansoko.graphics.text import draw_text, text_size, TextStyle
from bansoko.gui.input import VirtualButton
from bansoko.gui.navigator import ScreenController, BaseScreenController
from bansoko.gui.screen import Screen


class MenuItem(ABC):
    """An abstract, base class for all menu items controlled by MenuScreen."""

    def __init__(self, controller_to_switch_to: Callable[[], Optional[ScreenController]]):
        self.controller_to_switch_to = controller_to_switch_to

    @property
    @abstractmethod
    def disabled(self) -> bool:
        """Is menu item disabled.

        It is not possible to perform action on disabled menu items.
        """

    @property
    @abstractmethod
    def size(self) -> Size:
        """Size (in pixels) of the menu item.

        This property is used during layout
        """

    @abstractmethod
    def draw(self, position: Point, selected: bool = False) -> None:
        """Draw menu item at given position.

        :param position: position to draw menu item at
        :param selected: should the item be drawn as selected
        """

    def perform_action(self) -> Optional[ScreenController]:
        """Perform action tied up to the menu item.

        Navigation between game screens is controlled by return value.

        :return: instance of Screen class - switch to new screen controller *OR*
        None - switch to previous screen controller (exit menu screen)
        """
        return self.controller_to_switch_to()


MENU_TEXT_NORMAL = TextStyle(color=7, shadow_color=1)
MENU_TEXT_SELECTED = TextStyle(color=10, shadow_color=1)
MENU_TEXT_DISABLED = TextStyle(color=12, shadow_color=1)


class TextMenuItem(MenuItem):
    """Text-based menu item.

    It contains only label, which changes color when item is selected.
    """

    def __init__(self, text: str,
                 controller_to_switch_to: Callable[[], Optional[ScreenController]]):
        super().__init__(controller_to_switch_to)
        self.text = text

    @property
    def disabled(self) -> bool:
        return False

    @property
    def size(self) -> Size:
        return text_size(self._get_item_text(selected=True), MENU_TEXT_NORMAL).enlarge(2)

    def draw(self, position: Point, selected: bool = False) -> None:
        if self.disabled:
            style = MENU_TEXT_DISABLED
        elif selected:
            style = MENU_TEXT_SELECTED
        else:
            style = MENU_TEXT_NORMAL
        draw_text(position, self._get_item_text(selected), style)

    def _get_item_text(self, selected: bool = False) -> str:
        return ("* " if selected else "  ") + self.text


@dataclass(frozen=True)
class MenuLayout:
    """Menu layout configuration.

    Attributes:
        columns - number of visible columns in a single row of the menu
        rows - number of visible rows in the menu (if None it will be defaulted to total rows)
        position - screen-space position of the menu (if None menu will be centered on screen)
                   if one of the coordinates (x or y) is equal to -1 then menu will be centered
                   on screen in appropriate axis (horizontal or vertical)
        item_space - space between items in the menu
    """

    columns: int = 1
    rows: Optional[int] = None
    position: Optional[Point] = None
    item_space: Size = Size(0, 0)


@dataclass(frozen=True)
class Menu:
    """Menu is a list of options, user can navigate and choose from.

    Attributes:
        items - collection of menu items
        item_size - standardised size of menu item
        item_space - space between items in the menu
        columns - number of visible columns in a single row of the menu
        rows - number of visible rows in the menu
        position - screen-space position of the menu
    """

    items: Tuple[MenuItem, ...]
    item_size: Size
    item_space: Size
    columns: int
    rows: int
    position: Point

    @classmethod
    def with_defaults(cls, items: Tuple[MenuItem, ...],
                      layout: MenuLayout = MenuLayout()) -> "Menu":
        """Construct menu based on defaults.

        :param items: collection of menu items
        :param layout: layout information of the menu
        :return: newly created instance of Menu
        """
        item_size = reduce(max_size, [item.size for item in items])
        total_rows = -(-len(items) // layout.columns)
        calculated_rows = min(layout.rows, total_rows) if layout.rows else total_rows
        calculated_size = Size(
            layout.columns * item_size.width + (layout.columns - 1) * layout.item_space.width,
            calculated_rows * item_size.height + (calculated_rows - 1) * layout.item_space.height)
        centered_position = center_in_rect(calculated_size).position

        if layout.position:
            x = layout.position.x if layout.position.x >= 0 else centered_position.x
            y = layout.position.y if layout.position.y >= 0 else centered_position.y
            menu_position = Point(x, y)
        else:
            menu_position = centered_position

        return Menu(
            items=items,
            item_size=item_size,
            item_space=layout.item_space,
            columns=layout.columns,
            rows=calculated_rows,
            position=menu_position)

    @property
    def total_rows(self) -> int:
        """Total number of rows in the menu."""
        return -(-len(self.items) // self.columns)

    @property
    def items_on_page(self) -> int:
        """Number of items visible on single menu page."""
        return self.columns * self.rows


class MenuController(BaseScreenController):
    """MenuController is a screen controller containing configurable menu.

    Attributes:
        items - collection of all menu items that are going to be
        item_size - calculated maximum size of all menu items
        config - configuration the menu is initialized with
        position - screen-space position of the menu
        selected_item - index of currently selected menu item
        top_row - the very firs, top row that is visible when menu is drawn (it changes during
                  scrolling)
    """

    def __init__(self, menu: Menu, allow_going_back: bool = False,
                 screen: Optional[Screen] = None, semi_transparent: bool = False) -> None:
        super().__init__(semi_transparent=semi_transparent, screen=screen)
        self.menu = menu
        self.allow_going_back = allow_going_back
        self.top_row = 0
        self.selected_item = 0

    @property
    def scrollbar_size(self) -> float:
        """Size of the scroll bar relative to total number of menu rows.

        :return: Value from 0.0 to 1.0 describing the relation of the number of visible rows to
                 the number of all rows in the menu
        """
        return self.menu.rows / self.menu.total_rows

    @property
    def scrollbar_position(self) -> float:
        """Position of the scroll bar relative to total number of menu rows.

        :return: Value from 0.0 to 1.0 describing the relation of first visible row (top row) to
                 the number of all rows in the menu
        """
        return self.top_row / self.menu.total_rows

    @property
    def visible_items(self) -> Iterable[MenuItem]:
        """Collection of all visible menu items with respect to scroll bar position."""
        top_left_item = self.top_row * self.menu.columns
        bottom_left_item = min(
            (self.top_row + self.menu.rows) * self.menu.columns, len(self.menu.items))
        return islice(self.menu.items, top_left_item, bottom_left_item)

    def select_and_scroll_to_item(self, item: int) -> None:
        """Select menu item with given number and scroll menu to be sure that it's visible.

        :param item: item to be selected
        """
        if item < 0:
            self.selected_item = 0
        elif item >= len(self.menu.items):
            self.selected_item = len(self.menu.items) - 1
        else:
            self.selected_item = item

        self.scroll_to_item(self.selected_item)

    def scroll_to_item(self, item: int) -> None:
        """Scroll menu to specified item."""
        self.top_row = min(item // self.menu.columns, self.menu.total_rows - self.menu.rows)

    def update(self, dt_in_ms: float) -> Optional[ScreenController]:
        super().update(dt_in_ms)

        if self.input.is_button_pressed(VirtualButton.BACK) and self.allow_going_back:
            return None

        if not self.menu.items:
            return self

        selected_item_disabled = self.menu.items[self.selected_item].disabled
        if self.input.is_button_pressed(VirtualButton.SELECT) and not selected_item_disabled:
            return self.menu.items[self.selected_item].perform_action()

        if self.input.is_button_pressed(VirtualButton.UP):
            self._move_selection_up()
        elif self.input.is_button_pressed(VirtualButton.DOWN):
            self._move_selection_down()
        elif self.input.is_button_pressed(VirtualButton.LEFT):
            self._move_selection_left()
        elif self.input.is_button_pressed(VirtualButton.RIGHT):
            self._move_selection_right()
        elif self.input.is_button_pressed(VirtualButton.HOME):
            self._select_first()
        elif self.input.is_button_pressed(VirtualButton.END):
            self._select_last()
        elif self.input.is_button_pressed(VirtualButton.PAGE_UP):
            self._move_selection_page_up()
        elif self.input.is_button_pressed(VirtualButton.PAGE_DOWN):
            self._move_selection_page_down()

        return self

    def draw(self, draw_as_secondary: bool = False) -> None:
        super().draw(draw_as_secondary)

        for i, item in enumerate(self.visible_items):
            item_space = self.menu.item_space
            calculated_item_size = self.menu.item_size.enlarge(item_space.width, item_space.height)
            position = self.menu.position.offset(Point(
                (i % self.menu.columns) * calculated_item_size.width,
                (i // self.menu.columns) * calculated_item_size.height))
            item.draw(position, (self.top_row * self.menu.columns) + i == self.selected_item)

    def _move_selection_up(self) -> None:
        selected_row = self.selected_item // self.menu.columns
        move_up_possible = (selected_row > 0)
        if move_up_possible:
            self.selected_item = self.selected_item - self.menu.columns
            self.top_row = min(self.top_row, selected_row - 1)

    def _move_selection_down(self) -> None:
        selected_row = self.selected_item // self.menu.columns
        move_down_possible = (selected_row < (len(self.menu.items) - 1) // self.menu.columns)
        if move_down_possible:
            self.selected_item = min(
                self.selected_item + self.menu.columns, len(self.menu.items) - 1)
            if selected_row + 1 >= self.top_row + self.menu.rows:
                self.top_row += 1

    def _move_selection_left(self) -> None:
        selected_column = self.selected_item % self.menu.columns
        move_left_possible = (selected_column > 0)
        if move_left_possible:
            self.selected_item -= 1

    def _move_selection_right(self) -> None:
        selected_column = self.selected_item % self.menu.columns
        move_right_possible = (selected_column < self.menu.columns - 1) and \
                              (self.selected_item + 1 < len(self.menu.items))
        if move_right_possible:
            self.selected_item += 1

    def _select_first(self) -> None:
        self.select_and_scroll_to_item(0)

    def _select_last(self) -> None:
        self.select_and_scroll_to_item(len(self.menu.items) - 1)

    def _move_selection_page_up(self) -> None:
        self.select_and_scroll_to_item(self.selected_item - self.menu.items_on_page)

    def _move_selection_page_down(self) -> None:
        self.select_and_scroll_to_item(self.selected_item + self.menu.items_on_page)
