"""
Module for game menus management.
"""
import pyxel
from typing import Callable, List, NamedTuple, Optional

from graphics.screen import Screen


class MenuItem(NamedTuple):
    label: str
    screen_to_switch_to: Callable[[None], Optional[Screen]]


class Menu:
    def __init__(self, parent_screen: Screen, menu_items: List[MenuItem]):
        self.parent_screen = parent_screen
        self.menu_items = menu_items
        self.selected = 0

    def update(self) -> Optional[Screen]:
        if pyxel.btnp(pyxel.KEY_DOWN, 10, 5) or pyxel.btnp(pyxel.GAMEPAD_1_DOWN, 10, 5):
            self.selected = (self.selected + 1) % len(self.menu_items)
        if pyxel.btnp(pyxel.KEY_UP, 10, 5) or pyxel.btnp(pyxel.GAMEPAD_1_UP, 10, 5):
            self.selected = (self.selected - 1) % len(self.menu_items)
        if pyxel.btnp(pyxel.KEY_ENTER) or pyxel.btnp(pyxel.GAMEPAD_1_A):
            return self.menu_items[self.selected].screen_to_switch_to()
        if pyxel.btnp(pyxel.KEY_ESCAPE) or pyxel.btnp(pyxel.GAMEPAD_1_B):
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
