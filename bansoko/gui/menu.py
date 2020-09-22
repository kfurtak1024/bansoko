"""Module for game menus management."""
from abc import ABC, abstractmethod
from functools import reduce
from itertools import islice
from typing import Callable, List, Optional, Iterable

from bansoko.graphics import Size, Point, max_size, center_in_rect
from bansoko.graphics.background import Background
from bansoko.graphics.text import draw_text, text_size, TextStyle
from bansoko.gui.input import InputSystem, VirtualButton
from bansoko.gui.screen import Screen


class MenuItem(ABC):
    """An abstract, base class for all menu items controlled by MenuScreen."""

    @property
    @abstractmethod
    def disabled(self) -> bool:
        pass

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

    @abstractmethod
    def perform_action(self) -> Optional[Screen]:
        """Perform action tied up to the menu item.

        Navigation between game screens is controlled by return value.

        :return: instance of Screen class - switch to new screen *OR* None - switch to previous
        screen (exit menu screen)
        """


# TODO: Add horizontal space
class TextMenuItem(MenuItem):
    """Text-based menu item.

    It contains only label, which changes color when item is selected.
    """

    def __init__(self, text: str, screen_to_switch_to: Callable[[], Optional[Screen]]):
        self.text = text
        self.text_style = TextStyle(color=7, shadow_color=1)
        self.selected_text_style = TextStyle(color=10, shadow_color=1)
        self.disabled_text_style = TextStyle(color=12, shadow_color=1)
        self.screen_to_switch_to = screen_to_switch_to

    @property
    def disabled(self) -> bool:
        return False

    @property
    def size(self) -> Size:
        return text_size(self._get_item_text(selected=True), self.text_style).enlarge(2)

    def draw(self, position: Point, selected: bool = False) -> None:
        if self.disabled:
            style = self.disabled_text_style
        elif selected:
            style = self.selected_text_style
        else:
            style = self.text_style
        draw_text(position, self._get_item_text(selected), style)

    def perform_action(self) -> Optional[Screen]:
        return self.screen_to_switch_to()

    def _get_item_text(self, selected: bool = False) -> str:
        return ("* " if selected else "  ") + self.text


class MenuScreen(Screen):
    def __init__(self, items: List[MenuItem], columns: int = 1, rows: Optional[int] = None,
                 allow_going_back: bool = False, background: Optional[Background] = None):
        super().__init__(background)
        self.items = items
        self.item_size = reduce(max_size, [item.size for item in self.items])
        self.columns = columns
        self.rows = rows if rows else -(-len(items) // columns)
        self.top_row = 0
        self.selected_item = 0
        self.allow_going_back = allow_going_back
        self.input = InputSystem()

    def activate(self) -> None:
        self.input.reset()

    def update(self) -> Optional[Screen]:
        self.input.update()
        if self.input.is_button_pressed(VirtualButton.BACK) and self.allow_going_back:
            return None
        if not self.items:
            return self
        selected_item_disabled = self.items[self.selected_item].disabled
        if self.input.is_button_pressed(VirtualButton.SELECT) and not selected_item_disabled:
            return self.items[self.selected_item].perform_action()

        selected_row = self.selected_item // self.columns

        move_up_possible = (selected_row > 0)
        if self.input.is_button_pressed(VirtualButton.UP) and move_up_possible:
            self.selected_item = self.selected_item - self.columns
            self.top_row = min(self.top_row, selected_row - 1)

        move_down_possible = (selected_row < (len(self.items) - 1) // self.columns)
        if self.input.is_button_pressed(VirtualButton.DOWN) and move_down_possible:
            self.selected_item = min(self.selected_item + self.columns, len(self.items) - 1)
            if selected_row + 1 >= self.top_row + self.rows:
                self.top_row += 1

        selected_column = self.selected_item % self.columns

        move_left_possible = (selected_column > 0)
        if self.input.is_button_pressed(VirtualButton.LEFT) and move_left_possible:
            self.selected_item = self.selected_item - 1

        move_right_possible = (selected_column < self.columns - 1) and \
                              (self.selected_item + 1 < len(self.items))
        if self.input.is_button_pressed(VirtualButton.RIGHT) and move_right_possible:
            self.selected_item = self.selected_item + 1

        return self

    def draw(self) -> None:
        super().draw()

        start_position = center_in_rect(
            Size(self.columns * self.item_size.width, self.rows * self.item_size.height))

        for i, item in enumerate(self.visible_items):
            position = Point(start_position.x + (i % self.columns) * self.item_size.width,
                             start_position.y + (i // self.columns) * self.item_size.height)
            item.draw(position, (self.top_row * self.columns) + i == self.selected_item)

    @property
    def visible_items(self) -> Iterable[MenuItem]:
        top_left_item = self.top_row * self.columns
        bottom_left_item = min((self.top_row + self.rows) * self.columns, len(self.items))
        return islice(self.items, top_left_item, bottom_left_item)
