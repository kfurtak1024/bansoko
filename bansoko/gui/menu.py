"""
Module for game menus management.
"""
from typing import Callable, List, NamedTuple, Optional

import pyxel

from graphics import center_in_rect, Rect
from graphics.text import draw_text, text_size, TextAttributes
from gui.screen import Screen

BUTTON_HOLD_TIME = 10
BUTTON_PERIOD_TIME = 5


def _is_up_pressed() -> bool:
    return _is_button_pressed(pyxel.KEY_UP) \
           or _is_button_pressed(pyxel.GAMEPAD_1_UP)


def _is_down_pressed() -> bool:
    return _is_button_pressed(pyxel.KEY_DOWN) \
           or _is_button_pressed(pyxel.GAMEPAD_1_DOWN)


def _is_home_pressed() -> bool:
    return _is_button_pressed(pyxel.KEY_HOME)


def _is_end_pressed() -> bool:
    return _is_button_pressed(pyxel.KEY_END)


def _is_select_pressed() -> bool:
    return pyxel.btnp(pyxel.KEY_ENTER) or pyxel.btnp(pyxel.GAMEPAD_1_A)


def _is_back_pressed() -> bool:
    return pyxel.btnp(pyxel.KEY_ESCAPE) or pyxel.btnp(pyxel.GAMEPAD_1_B)


def _is_button_pressed(button: int) -> bool:
    return pyxel.btnp(button, BUTTON_HOLD_TIME, BUTTON_PERIOD_TIME)


class MenuItem(NamedTuple):
    label: str
    screen_to_switch_to: Callable[[None], Optional[Screen]]


class Menu:
    def __init__(self, parent_screen: Screen, menu_items: List[MenuItem]):
        self.parent_screen = parent_screen
        self.menu_items = menu_items
        self.selected = 0

    def update(self) -> Optional[Screen]:
        if _is_select_pressed():
            return self.menu_items[self.selected].screen_to_switch_to()
        if _is_back_pressed():
            return None
        if _is_down_pressed():
            self.selected = (self.selected + 1) % len(self.menu_items)
        if _is_up_pressed():
            self.selected = (self.selected - 1) % len(self.menu_items)
        if _is_home_pressed():
            self.selected = 0
        if _is_end_pressed():
            self.selected = len(self.menu_items) - 1
        return self.parent_screen

    def draw(self):
        menu_text = ""

        for i in range(len(self.menu_items)):
            prefix = "#9* " if self.selected == i else "#7  "
            menu_text += prefix + self.menu_items[i].label + "\n"

        text_attrib = TextAttributes(shadow=True, vertical_space=3)
        size = text_size(menu_text, text_attrib)
        pos = center_in_rect(size, Rect(0, 0, pyxel.width, pyxel.height))
        draw_text(pos.x, pos.y, menu_text, text_attrib)
