"""Module for game menus management."""
from abc import ABC, abstractmethod
from functools import reduce
from itertools import islice
from typing import Callable, Optional, Iterable, Tuple, NamedTuple

from bansoko.graphics import Size, Point, max_size, center_in_rect
from bansoko.graphics.background import Background
from bansoko.graphics.text import draw_text, text_size, TextStyle
from bansoko.gui.input import VirtualButton
from bansoko.gui.screen import Screen


class MenuItem(ABC):
    """An abstract, base class for all menu items controlled by MenuScreen."""

    def __init__(self, screen_to_switch_to: Callable[[], Optional[Screen]]):
        self.screen_to_switch_to = screen_to_switch_to

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

    def perform_action(self) -> Optional[Screen]:
        """Perform action tied up to the menu item.

        Navigation between game screens is controlled by return value.

        :return: instance of Screen class - switch to new screen *OR* None - switch to previous
        screen (exit menu screen)
        """
        return self.screen_to_switch_to()


MENU_TEXT_NORMAL = TextStyle(color=7, shadow_color=1)
MENU_TEXT_SELECTED = TextStyle(color=10, shadow_color=1)
MENU_TEXT_DISABLED = TextStyle(color=12, shadow_color=1)


class TextMenuItem(MenuItem):
    """Text-based menu item.

    It contains only label, which changes color when item is selected.
    """

    def __init__(self, text: str, screen_to_switch_to: Callable[[], Optional[Screen]]):
        super().__init__(screen_to_switch_to)
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


class MenuConfig(NamedTuple):
    """The configuration of menu screen.

    Attributes:
        columns - number of visible columns of menu
        rows - number of visible rows of menu
        allow_going_back - is it allowed to go back to the previous screen from the menu screen
        background - the background to drawn the menu screen with
        semi_transparent - semi transparent screens are drawn on top of the top screen from screen
                           stack
        position - screen-space position of the menu
    """
    columns: int = 1
    rows: Optional[int] = None
    allow_going_back: bool = False
    background: Optional[Background] = None
    semi_transparent: bool = False
    position: Optional[Point] = None


class MenuScreen(Screen):
    def __init__(self, items: Tuple[MenuItem, ...], config: MenuConfig, selected_item: int = 0):
        super().__init__(semi_transparent=config.semi_transparent, background=config.background)
        self.items = items
        self.item_size = reduce(max_size, [item.size for item in self.items])
        self.config = config
        self.position = config.position if config.position else center_in_rect(
            Size(self.columns * self.item_size.width, self.rows * self.item_size.height))
        self.selected_item = selected_item
        self.top_row = 0
        self.scroll_to_item(self.selected_item)

    @property
    def columns(self) -> int:
        """The number of visible columns in a single row of the menu."""
        return self.config.columns

    @property
    def rows(self) -> int:
        """The number of visible rows in the menu."""
        return self.config.rows if self.config.rows else self.total_rows

    @property
    def total_rows(self) -> int:
        """Total number of rows in the menu."""
        return -(-len(self.items) // self.columns)

    @property
    def scrollbar_size(self) -> float:
        """Size of the scroll bar relative to total number of menu rows.

        :return: Value from 0.0 to 1.0 describing the relation of the number of visible rows to
                 the number of all rows in the menu
        """
        return self.rows / self.total_rows

    @property
    def scrollbar_position(self) -> float:
        """Position of the scroll bar relative to total number of menu rows.

        :return: Value from 0.0 to 1.0 describing the relation of first visible row (top row) to
                 the number of all rows in the menu
        """
        return self.top_row / self.total_rows

    @property
    def visible_items(self) -> Iterable[MenuItem]:
        """Collection of all visible menu items with respect to scroll bar position."""
        top_left_item = self.top_row * self.columns
        bottom_left_item = min((self.top_row + self.rows) * self.columns, len(self.items))
        return islice(self.items, top_left_item, bottom_left_item)

    def scroll_to_item(self, item: int) -> None:
        """Scroll menu to specified item."""
        self.top_row = min(item // self.columns, self.total_rows - self.rows)

    def update(self) -> Optional[Screen]:
        super().update()

        if self.input.is_button_pressed(VirtualButton.BACK) and self.config.allow_going_back:
            return None

        if not self.items:
            return self

        selected_item_disabled = self.items[self.selected_item].disabled
        if self.input.is_button_pressed(VirtualButton.SELECT) and not selected_item_disabled:
            return self.items[self.selected_item].perform_action()

        if self.input.is_button_pressed(VirtualButton.UP):
            self._move_selection_up()
        elif self.input.is_button_pressed(VirtualButton.DOWN):
            self._move_selection_down()
        elif self.input.is_button_pressed(VirtualButton.LEFT):
            self._move_selection_left()
        elif self.input.is_button_pressed(VirtualButton.RIGHT):
            self._move_selection_right()

        return self

    def draw(self, draw_as_secondary: bool = False) -> None:
        super().draw(draw_as_secondary)

        for i, item in enumerate(self.visible_items):
            position = Point(self.position.x + (i % self.columns) * self.item_size.width,
                             self.position.y + (i // self.columns) * self.item_size.height)
            item.draw(position, (self.top_row * self.columns) + i == self.selected_item)

    def _move_selection_up(self) -> None:
        selected_row = self.selected_item // self.columns
        move_up_possible = (selected_row > 0)
        if move_up_possible:
            self.selected_item = self.selected_item - self.columns
            self.top_row = min(self.top_row, selected_row - 1)

    def _move_selection_down(self) -> None:
        selected_row = self.selected_item // self.columns
        move_down_possible = (selected_row < (len(self.items) - 1) // self.columns)
        if move_down_possible:
            self.selected_item = min(self.selected_item + self.columns, len(self.items) - 1)
            if selected_row + 1 >= self.top_row + self.rows:
                self.top_row += 1

    def _move_selection_left(self) -> None:
        selected_column = self.selected_item % self.columns
        move_left_possible = (selected_column > 0)
        if move_left_possible:
            self.selected_item -= 1

    def _move_selection_right(self) -> None:
        selected_column = self.selected_item % self.columns
        move_right_possible = (selected_column < self.columns - 1) and \
                              (self.selected_item + 1 < len(self.items))
        if move_right_possible:
            self.selected_item += 1
