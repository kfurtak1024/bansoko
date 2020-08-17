"""
Module for game menus management.
"""
from abc import ABC, abstractmethod
from functools import reduce
from itertools import islice
from typing import Callable, List, Optional, Iterable

from bansoko.graphics import Size, Point, max_size, center_in_rect
from bansoko.graphics.text import draw_text, text_size, TextStyle
from bansoko.gui.input import InputSystem, VirtualButton
from bansoko.gui.screen import Screen
from graphics.background import Background


class MenuItem(ABC):
    @abstractmethod
    def size(self) -> Size:
        pass

    @abstractmethod
    def draw(self, position: Point, selected: bool = False) -> None:
        pass

    @abstractmethod
    def perform_action(self) -> Screen:
        pass


# TODO: Add horizontal space
class TextMenuItem(MenuItem):
    def __init__(self, text: str, screen_to_switch_to: Callable[[], Optional[Screen]]):
        self.text = text
        self.text_style = TextStyle(color=7, shadow=True)
        self.selected_text_style = TextStyle(color=10, shadow=True)
        self.screen_to_switch_to = screen_to_switch_to

    def size(self) -> Size:
        return text_size(self.__get_item_text(selected=True), self.text_style)

    def draw(self, position: Point, selected: bool = False) -> None:
        style = self.selected_text_style if selected else self.text_style
        draw_text(position.x, position.y, self.__get_item_text(selected), style)

    def perform_action(self) -> Screen:
        return self.screen_to_switch_to()

    def __get_item_text(self, selected: bool = False) -> str:
        return ("* " if selected else "  ") + self.text


class MenuScreen(Screen):
    items: List[MenuItem]
    item_size: Size
    columns: int
    rows: int
    top_item: int
    selected_item: int

    def __init__(self, items: List[MenuItem], columns: int = 1, rows: int = None,
                 background: Optional[Background] = None):
        super().__init__(background)
        self.items = items
        self.item_size = reduce(max_size, [item.size() for item in self.items])
        self.columns = columns
        self.rows = rows if rows else -(-len(items) // columns)
        self.top_item = 0
        self.selected_item = 0
        self.background = background
        self.input = InputSystem()

    def activate(self) -> None:
        self.input.reset()

    def update(self) -> Optional[Screen]:
        self.input.update()
        if self.input.is_button_pressed(VirtualButton.BACK):
            return None
        if not self.items:
            return self
        if self.input.is_button_pressed(VirtualButton.SELECT):
            return self.items[self.selected_item].perform_action()

        selected_row = self.selected_item // self.columns

        move_up_possible = (selected_row > 0)
        if self.input.is_button_pressed(VirtualButton.UP) and move_up_possible:
            self.selected_item = self.selected_item - self.columns

        move_down_possible = (selected_row < self.rows - 1) and (
                self.selected_item + self.columns < len(self.items))
        if self.input.is_button_pressed(VirtualButton.DOWN) and move_down_possible:
            self.selected_item = self.selected_item + self.columns

        selected_column = self.selected_item % self.columns

        move_left_possible = (selected_column > 0)
        if self.input.is_button_pressed(VirtualButton.LEFT) and move_left_possible:
            self.selected_item = self.selected_item - 1

        move_right_possible = (selected_column < self.columns - 1) and (
                self.selected_item + 1 < len(self.items))
        if self.input.is_button_pressed(VirtualButton.RIGHT) and move_right_possible:
            self.selected_item = self.selected_item + 1

        return self

    def draw(self) -> None:
        super().draw()

        start_position = center_in_rect(
            Size(self.columns * self.item_size.width, self.rows * self.item_size.height))

        for i, item in enumerate(self.__visible_items()):
            position = Point(start_position.x + (i % self.columns) * self.item_size.width,
                             start_position.y + (i // self.columns) * self.item_size.height)
            item.draw(position, i == self.selected_item)

    def __visible_items(self) -> Iterable[MenuItem]:
        bottom_item = min(self.top_item + self.columns * self.rows, len(self.items))
        return islice(self.items, self.top_item, bottom_item)
