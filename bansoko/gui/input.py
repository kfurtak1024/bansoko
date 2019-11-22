from typing import Dict, List

import pyxel


class InputSystem:
    BUTTON_HOLD_TIME: int = 10
    BUTTON_PERIOD_TIME: int = 2

    NAV_BUTTONS: List[int] = [
        pyxel.KEY_UP,
        pyxel.GAMEPAD_1_UP,
        pyxel.KEY_DOWN,
        pyxel.GAMEPAD_1_DOWN,
        pyxel.KEY_LEFT,
        pyxel.GAMEPAD_1_LEFT,
        pyxel.KEY_RIGHT,
        pyxel.GAMEPAD_1_RIGHT
    ]

    pressed_buttons: Dict[int, int]

    def __init__(self):
        self.pressed_buttons = {}

    def update(self) -> None:
        for button in self.NAV_BUTTONS:
            if pyxel.btn(button):
                if button not in self.pressed_buttons and not pyxel.btnp(button):
                    return
                self.__press_button(button)
            else:
                self.__depress_button(button)

    def reset(self):
        self.pressed_buttons.clear()

    def is_up_pressed(self) -> bool:
        return self.__is_button_pressed(pyxel.KEY_UP) \
            or self.__is_button_pressed(pyxel.GAMEPAD_1_UP)

    def is_down_pressed(self) -> bool:
        return self.__is_button_pressed(pyxel.KEY_DOWN) \
            or self.__is_button_pressed(pyxel.GAMEPAD_1_DOWN)

    def is_left_pressed(self) -> bool:
        return self.__is_button_pressed(pyxel.KEY_LEFT) \
            or self.__is_button_pressed(pyxel.GAMEPAD_1_LEFT)

    def is_right_pressed(self) -> bool:
        return self.__is_button_pressed(pyxel.KEY_RIGHT) \
            or self.__is_button_pressed(pyxel.GAMEPAD_1_RIGHT)

    @staticmethod
    def is_home_pressed() -> bool:
        return pyxel.btnp(pyxel.KEY_HOME)

    @staticmethod
    def is_end_pressed() -> bool:
        return pyxel.btnp(pyxel.KEY_END)

    @staticmethod
    def is_select_pressed() -> bool:
        return pyxel.btnp(pyxel.KEY_ENTER) or pyxel.btnp(pyxel.GAMEPAD_1_A)

    @staticmethod
    def is_back_pressed() -> bool:
        return pyxel.btnp(pyxel.KEY_ESCAPE) or pyxel.btnp(pyxel.GAMEPAD_1_B)

    def __is_button_pressed(self, button: int) -> bool:
        if button not in self.pressed_buttons:
            return False
        hold_time = self.pressed_buttons[button]
        if hold_time == 0:
            return True
        if hold_time < self.BUTTON_HOLD_TIME:
            return False
        if (hold_time - self.BUTTON_HOLD_TIME) % self.BUTTON_PERIOD_TIME == 0:
            return True

        return False

    def __press_button(self, button: int):
        self.pressed_buttons[button] = self.pressed_buttons.get(button, -1) + 1

    def __depress_button(self, button: int):
        if button in self.pressed_buttons:
            del self.pressed_buttons[button]
