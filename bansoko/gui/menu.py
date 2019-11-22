"""
Module for game menus management.
"""
from typing import Callable, List, NamedTuple, Optional

import pyxel

from graphics import center_in_rect, Rect
from graphics.text import draw_text, text_size, TextAttributes
from gui.input import InputSystem
from gui.screen import Screen


class MenuItem(NamedTuple):
    label: str
    screen_to_switch_to: Callable[[None], Optional[Screen]]


class Menu:
    def __init__(self, parent_screen: Screen, menu_items: List[MenuItem]):
        self.parent_screen = parent_screen
        self.menu_items = menu_items
        self.selected = 0
        self.input = InputSystem()

    def update(self) -> Optional[Screen]:
        self.input.update()
        if self.input.is_select_pressed():
            return self.menu_items[self.selected].screen_to_switch_to()
        if self.input.is_back_pressed():
            return None
        if self.input.is_down_pressed():
            self.selected = (self.selected + 1) % len(self.menu_items)
        if self.input.is_up_pressed():
            self.selected = (self.selected - 1) % len(self.menu_items)
        if self.input.is_home_pressed():
            self.selected = 0
        if self.input.is_end_pressed():
            self.selected = len(self.menu_items) - 1
        return self.parent_screen

    def draw(self) -> None:
        menu_text = ""

        for i in range(len(self.menu_items)):
            prefix = "#9* " if self.selected == i else "#7  "
            menu_text += prefix + self.menu_items[i].label + "\n"

        text_attrib = TextAttributes(shadow=True, vertical_space=3)
        size = text_size(menu_text, text_attrib)
        pos = center_in_rect(size, Rect(0, 0, pyxel.width, pyxel.height))
        draw_text(pos.x, pos.y, menu_text, text_attrib)
