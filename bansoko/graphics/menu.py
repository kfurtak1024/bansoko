"""
Module for game menus management.
"""
from typing import Callable, List, NamedTuple, Optional

import pyxel

from graphics.screen import Screen

BUTTON_HOLD_TIME = 10
BUTTON_PERIOD_TIME = 5


def _is_up_pressed() -> bool:
    return _is_button_pressed(pyxel.KEY_UP) \
           or _is_button_pressed(pyxel.GAMEPAD_1_UP)


def _is_down_pressed() -> bool:
    return _is_button_pressed(pyxel.KEY_DOWN) \
           or _is_button_pressed(pyxel.GAMEPAD_1_DOWN)


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
        if _is_down_pressed():
            self.selected = (self.selected + 1) % len(self.menu_items)
        if _is_up_pressed():
            self.selected = (self.selected - 1) % len(self.menu_items)
        if _is_select_pressed():
            return self.menu_items[self.selected].screen_to_switch_to()
        if _is_back_pressed():
            return None
        return self.parent_screen

    def draw(self):
        i = 0
        y = 32
        for menu_item in self.menu_items:
            prefix = "* " if self.selected == i else "  "
            pyxel.text(16, y, prefix + str(i + 1) + ") " + menu_item.label, 7)
            y += 8
            i = i + 1
