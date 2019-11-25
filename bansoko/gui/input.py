"""
Module exposing basic system for input handling.
"""
from enum import unique, IntFlag
from typing import Dict, List

import pyxel


@unique
class VirtualButton(IntFlag):
    """
    Virtual button of a virtual game controller.
    """
    UP = 0x01
    DOWN = 0x02
    LEFT = 0x04
    RIGHT = 0x08
    SELECT = 0x10
    BACK = 0x20


class InputSystem:
    KEY_HOLD_TIME: int = 10
    KEY_PERIOD_TIME: int = 2
    BUTTONS_MAP: Dict[VirtualButton, List[int]] = {
        VirtualButton.UP: [pyxel.KEY_UP, pyxel.GAMEPAD_1_UP],
        VirtualButton.DOWN: [pyxel.KEY_DOWN, pyxel.GAMEPAD_1_DOWN],
        VirtualButton.LEFT: [pyxel.KEY_LEFT, pyxel.GAMEPAD_1_LEFT],
        VirtualButton.RIGHT: [pyxel.KEY_RIGHT, pyxel.GAMEPAD_1_RIGHT],
        VirtualButton.SELECT: [pyxel.KEY_ENTER, pyxel.GAMEPAD_1_A],
        VirtualButton.BACK: [pyxel.KEY_ESCAPE, pyxel.GAMEPAD_1_B]
    }

    pressed_keys: Dict[int, int]

    def __init__(self):
        self.pressed_keys = {}

    def is_button_pressed(self, button: VirtualButton) -> bool:
        """
        Test if given virtual button is "pressed".
        Button is "pressed" when:
            - in previous update frame it was up and now it's down *OR*
            - it is down for exactly KEY_HOLD_TIME (and was preceded be previous point) *OR*
            - in every KEY_PERIOD_TIME interval (and was preceded be previous point)

        Note that above is valid only if it was not interrupted by a reset call.
        Both KEY_HOLD_TIME and KEY_PERIOD_TIME are expressed in number of occurred update frames.

        Arguments:
            button - virtual button to be tested

        Returns:
            - true - if button was pressed,
            - false - otherwise
        """

        return any(self.__is_key_pressed(key) for key in self.BUTTONS_MAP[button])

    def is_button_down(self, button: VirtualButton) -> bool:
        """
        Test if given virtual button is down at the current update frame.

        Arguments:
            button - virtual button to be tested

        Returns:
            - true - if button is down in current update frame,
            - false - otherwise
        """

        return any(self.__is_key_down(key) for key in self.BUTTONS_MAP[button])

    def is_button_up(self, button: VirtualButton) -> bool:
        """
        Test if given virtual button is up at the current update frame.

        Arguments:
            button - virtual button to be tested

        Returns:
            - true - if button is up in current update frame,
            - false - otherwise
        """

        return not self.is_button_down(button)

    def update(self) -> None:
        """
        Update statuses of all watched keys.
        This needs to be called each frame.
        """

        watched_keys: List[int] = sum(self.BUTTONS_MAP.values(), [])
        for key in watched_keys:
            if pyxel.btn(key):
                if key not in self.pressed_keys and not pyxel.btnp(key):
                    return
                self.__press_key(key)
            else:
                self.__depress_key(key)

    def reset(self) -> None:
        """
        Reset the statuses of all watched keys.
        This should be called when focus switches to another screen.
        """

        self.pressed_keys.clear()

    def __is_key_pressed(self, key: int) -> bool:
        if pyxel.btn(pyxel.KEY_ALT):
            return False
        if key not in self.pressed_keys:
            return False
        hold_time = self.pressed_keys[key]
        if hold_time == 0:
            return True
        if hold_time < self.KEY_HOLD_TIME:
            return False
        if (hold_time - self.KEY_HOLD_TIME) % self.KEY_PERIOD_TIME == 0:
            return True
        return False

    def __is_key_down(self, key: int) -> bool:
        if pyxel.btn(pyxel.KEY_ALT):
            return False
        return key in self.pressed_keys

    def __press_key(self, key: int) -> None:
        self.pressed_keys[key] = self.pressed_keys.get(key, -1) + 1

    def __depress_key(self, key: int) -> None:
        if key in self.pressed_keys:
            del self.pressed_keys[key]
