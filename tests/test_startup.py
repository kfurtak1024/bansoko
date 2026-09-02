"""Tests for how the game reports a failure to open its window.

Pyxel needs OpenGL, and when it cannot get it the Rust layer raises a
PanicException whose text means nothing to a player. That happens before any
game screen exists, so the in-game error screen cannot be used to report it:
these are the only thing standing between a player and a raw Rust traceback.
"""
import logging
from typing import Any, List

import pytest

import bansoko.__main__ as game_main
from bansoko.__main__ import (GRAPHICS_ERROR_MESSAGE, can_reach_player_with_text,
                              initialize_display, is_graphics_failure,
                              report_startup_failure)


class FakePanic(BaseException):
    """Stand-in for pyo3_runtime.PanicException.

    That class cannot be imported (PyO3 creates it at runtime) and, like the
    real one, this derives from BaseException rather than Exception, which is
    exactly why a plain "except Exception" fails to catch it.
    """


# Messages seen in the wild: no display at all, and a virtual machine with no
# OpenGL driver.
@pytest.mark.parametrize("message", [
    "Failed to initialize SDL2: No available video device",
    "called glCreateShader but it was not loaded.",
    "Failed to create window: OpenGL support is either not configured in SDL",
    "CALLED GLCREATESHADER BUT IT WAS NOT LOADED",
])
def test_recognises_graphics_failures(message: str) -> None:
    """Real Pyxel graphics panics must be recognised, whatever their case."""
    assert is_graphics_failure(message)


@pytest.mark.parametrize("message", [
    "Unable to find Pyxel resource file",
    "some unrelated panic in another subsystem",
    "",
])
def test_ignores_unrelated_failures(message: str) -> None:
    """Anything else must not be mistaken for a graphics problem."""
    assert not is_graphics_failure(message)


def test_graphics_panic_becomes_a_clean_exit(monkeypatch: pytest.MonkeyPatch,
                                             capsys: pytest.CaptureFixture[str]) -> None:
    """A graphics panic exits cleanly with an explanation, not a traceback."""
    def explode(**_: Any) -> None:
        raise FakePanic("called glCreateShader but it was not loaded.")

    monkeypatch.setattr("bansoko.__main__.pyxel.init", explode)

    with pytest.raises(SystemExit) as exit_info:
        initialize_display()

    assert exit_info.value.code == 1
    reported = capsys.readouterr().err
    assert "needs OpenGL" in reported
    # The player is told what to do about it, and the raw detail is kept for
    # a bug report.
    assert "graphics drivers" in reported
    assert "glCreateShader" in reported


def test_other_failures_are_not_swallowed(monkeypatch: pytest.MonkeyPatch) -> None:
    """A failure that is not about graphics must propagate untouched.

    Dressing an unrelated crash up as a driver problem would send players
    chasing the wrong thing.
    """
    def explode(**_: Any) -> None:
        raise FakePanic("something else went badly wrong")

    monkeypatch.setattr("bansoko.__main__.pyxel.init", explode)

    with pytest.raises(FakePanic):
        initialize_display()


def test_keyboard_interrupt_is_not_swallowed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ctrl-C during start-up stays a KeyboardInterrupt."""
    def explode(**_: Any) -> None:
        raise KeyboardInterrupt()

    monkeypatch.setattr("bansoko.__main__.pyxel.init", explode)

    with pytest.raises(KeyboardInterrupt):
        initialize_display()


def test_failure_is_reported_to_stderr_and_the_log(
        capsys: pytest.CaptureFixture[str], caplog: pytest.LogCaptureFixture) -> None:
    """The message reaches both the player and the log file."""
    with caplog.at_level(logging.ERROR):
        report_startup_failure(GRAPHICS_ERROR_MESSAGE)

    assert "needs OpenGL" in capsys.readouterr().err
    assert any("needs OpenGL" in record.message for record in caplog.records)


def test_no_dialog_when_a_console_is_available(monkeypatch: pytest.MonkeyPatch) -> None:
    """A modal dialog must never appear where text would do.

    This is a regression test for a hung CI job: report_startup_failure used
    to open a message box on Windows unconditionally, and on a headless
    runner it waited forever for a click that was never coming. Under pytest
    there is always a console, so no dialog may be attempted.
    """
    shown: List[str] = []
    monkeypatch.setattr(game_main, "show_error_dialog", shown.append)

    report_startup_failure("something went wrong")

    assert not shown, "a modal dialog was opened during a console session"


def test_dialog_is_used_when_text_cannot_reach_the_player(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """With no console, the dialog is the only way to reach the player."""
    shown: List[str] = []
    monkeypatch.setattr(game_main, "show_error_dialog", shown.append)
    monkeypatch.setattr(game_main, "can_reach_player_with_text", lambda: False)

    report_startup_failure("something went wrong")

    assert shown == ["something went wrong"]


def test_text_always_reaches_the_player_off_windows(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Only Windows builds can end up without a usable console."""
    monkeypatch.setattr(game_main.sys, "platform", "linux")
    assert can_reach_player_with_text()
