"""Tests for the input system: which keys count as held, pressed and released.

Pyxel's key state is replaced with a set the test controls, so these run
without a window and say exactly which keys are down in each frame.
"""
# Requesting a fixture shadows the function that defines it. That is how
# pytest fixtures work, so the check is disabled for this file only.
# pylint: disable=redefined-outer-name
from typing import Set

import pytest

import pyxel

from bansoko.gui.input import InputSystem, VirtualButton


class FakeKeyboard:
    """The keys that are down, and the ones that went down this frame."""

    def __init__(self) -> None:
        self.down: Set[int] = set()
        self.just_pressed: Set[int] = set()

    def press(self, key: int) -> None:
        """Push a key down, as seen in the next frame."""
        self.down.add(key)
        self.just_pressed.add(key)

    def release(self, key: int) -> None:
        """Let a key go."""
        self.down.discard(key)

    def frame(self, input_system: InputSystem) -> None:
        """Run one update frame."""
        input_system.update()
        self.just_pressed.clear()


@pytest.fixture()
def keyboard(monkeypatch: pytest.MonkeyPatch) -> FakeKeyboard:
    """A keyboard standing in for Pyxel's."""
    fake = FakeKeyboard()
    monkeypatch.setattr(pyxel, "btn", lambda key: key in fake.down)
    monkeypatch.setattr(pyxel, "btnp", lambda key: key in fake.just_pressed)
    return fake


STALE_KEYS = sorted(InputSystem.WATCHED_KEYS - {pyxel.KEY_RIGHT})


def test_a_pressed_key_is_down_until_it_is_released(keyboard: FakeKeyboard) -> None:
    """The plain case: down while held, pressed only in the first frame."""
    input_system = InputSystem()

    keyboard.press(pyxel.KEY_RIGHT)
    keyboard.frame(input_system)
    assert input_system.is_button_down(VirtualButton.RIGHT)
    assert input_system.is_button_pressed(VirtualButton.RIGHT)

    keyboard.frame(input_system)
    assert input_system.is_button_down(VirtualButton.RIGHT)
    assert not input_system.is_button_pressed(VirtualButton.RIGHT)

    keyboard.release(pyxel.KEY_RIGHT)
    keyboard.frame(input_system)
    assert input_system.is_button_up(VirtualButton.RIGHT)


def test_a_key_held_across_a_reset_is_ignored_until_released(keyboard: FakeKeyboard) -> None:
    """The key that chose a menu item must not act on the screen it led to."""
    input_system = InputSystem()
    keyboard.press(pyxel.KEY_RETURN)
    keyboard.frame(input_system)

    input_system.reset()
    keyboard.frame(input_system)
    assert not input_system.is_button_down(VirtualButton.SELECT)

    keyboard.release(pyxel.KEY_RETURN)
    keyboard.frame(input_system)
    keyboard.press(pyxel.KEY_RETURN)
    keyboard.frame(input_system)
    assert input_system.is_button_pressed(VirtualButton.SELECT)


@pytest.mark.parametrize("stale_key", STALE_KEYS)
def test_a_stale_key_does_not_hide_a_new_press(keyboard: FakeKeyboard, stale_key: int) -> None:
    """Whichever key is still held from the last screen, a new one registers."""
    input_system = InputSystem()
    keyboard.down.add(stale_key)  # Held since before this screen was activated.
    keyboard.frame(input_system)

    keyboard.press(pyxel.KEY_RIGHT)
    keyboard.frame(input_system)
    assert input_system.is_button_down(VirtualButton.RIGHT)


@pytest.mark.parametrize("stale_key", STALE_KEYS)
def test_a_stale_key_does_not_keep_a_released_key_down(keyboard: FakeKeyboard,
                                                       stale_key: int) -> None:
    """Whichever key is still held from the last screen, a released one lets go."""
    input_system = InputSystem()
    keyboard.down.add(stale_key)  # Held since before this screen was activated.
    keyboard.press(pyxel.KEY_RIGHT)
    keyboard.frame(input_system)

    keyboard.release(pyxel.KEY_RIGHT)
    keyboard.frame(input_system)
    assert input_system.is_button_up(VirtualButton.RIGHT)
