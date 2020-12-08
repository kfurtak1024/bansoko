"""Module exposing basic system for input handling."""
from enum import unique, IntFlag
from typing import Dict, List, Set

import pyxel


@unique
class VirtualButton(IntFlag):
    """Virtual button of a virtual game controller."""

    UP = 0x001
    DOWN = 0x002
    LEFT = 0x004
    RIGHT = 0x008
    SELECT = 0x010
    BACK = 0x020
    START = 0x040
    ACTION = 0x080
    HOME = 0x100
    END = 0x200
    PAGE_UP = 0x400
    PAGE_DOWN = 0x800


class InputSystem:
    """InputSystem is a wrapper around Pyxel's input handling.

    It operates on VirtualButton which is an abstraction over physical buttons.
    InputSystem needs to be updated by calling update() method in each frame.
    """

    KEY_HOLD_TIME: int = 10
    KEY_PERIOD_TIME: int = 2
    BUTTONS_MAP: Dict[VirtualButton, List[int]] = {
        VirtualButton.UP: [pyxel.KEY_UP, pyxel.KEY_KP_8, pyxel.GAMEPAD_1_UP],
        VirtualButton.DOWN: [pyxel.KEY_DOWN, pyxel.KEY_KP_2, pyxel.GAMEPAD_1_DOWN],
        VirtualButton.LEFT: [pyxel.KEY_LEFT, pyxel.KEY_KP_4, pyxel.GAMEPAD_1_LEFT],
        VirtualButton.RIGHT: [pyxel.KEY_RIGHT, pyxel.KEY_KP_6, pyxel.GAMEPAD_1_RIGHT],
        VirtualButton.SELECT: [pyxel.KEY_ENTER, pyxel.KEY_KP_ENTER, pyxel.GAMEPAD_1_A],
        VirtualButton.BACK: [pyxel.KEY_ESCAPE, pyxel.GAMEPAD_1_B],
        VirtualButton.START: [pyxel.KEY_ESCAPE, pyxel.GAMEPAD_1_START],
        VirtualButton.ACTION: [pyxel.KEY_Z, pyxel.KEY_BACKSPACE, pyxel.GAMEPAD_1_B],
        VirtualButton.HOME: [pyxel.KEY_HOME],
        VirtualButton.END: [pyxel.KEY_END],
        VirtualButton.PAGE_UP: [pyxel.KEY_PAGE_UP],
        VirtualButton.PAGE_DOWN: [pyxel.KEY_PAGE_DOWN]
    }
    WATCHED_KEYS: Set[int] = set(sum(BUTTONS_MAP.values(), []))

    pressed_keys: Dict[int, int]

    def __init__(self) -> None:
        self.pressed_keys = {}

    def is_button_pressed(self, button: VirtualButton) -> bool:
        """Test if given virtual button is "pressed".

        Button is "pressed" when:
            - in previous update frame it was up and now it's down *OR*
            - it is down for exactly KEY_HOLD_TIME (and was preceded be previous point) *OR*
            - in every KEY_PERIOD_TIME interval (and was preceded be previous point)

        Note that above is valid only if it was not interrupted by a reset call.
        Both KEY_HOLD_TIME and KEY_PERIOD_TIME are expressed in number of occurred update frames.

        :param button: virtual button to be tested
        :return: True - if button was pressed *OR* False - otherwise
        """
        return any(self._is_key_pressed(key) for key in self.BUTTONS_MAP[button])

    def is_button_down(self, button: VirtualButton) -> bool:
        """Test if given virtual button is down at the current update frame.

        :param button: virtual button to be tested
        :return: True - if button is down in current update frame *OR* False - otherwise
        """
        return any(self._is_key_down(key) for key in self.BUTTONS_MAP[button])

    def is_button_up(self, button: VirtualButton) -> bool:
        """Test if given virtual button is up at the current update frame.

        :param button: virtual button to be tested
        :return: True - if button is up in current update frame *OR* False - otherwise
        """
        return not self.is_button_down(button)

    def update(self) -> None:
        """Update statuses of all watched keys.

        This needs to be called each frame.
        """
        for key in self.WATCHED_KEYS:
            if pyxel.btn(key):
                if key not in self.pressed_keys and not pyxel.btnp(key):
                    return
                self._press_key(key)
            else:
                self._depress_key(key)

    def reset(self) -> None:
        """Reset the statuses of all watched keys.

        This should be called when focus switches to another screen.
        """
        self.pressed_keys.clear()

    def _is_key_pressed(self, key: int) -> bool:
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

    def _is_key_down(self, key: int) -> bool:
        if pyxel.btn(pyxel.KEY_ALT):
            return False
        return key in self.pressed_keys

    def _press_key(self, key: int) -> None:
        self.pressed_keys[key] = self.pressed_keys.get(key, -1) + 1

    def _depress_key(self, key: int) -> None:
        if key in self.pressed_keys:
            del self.pressed_keys[key]
