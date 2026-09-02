"""Tests for how the game reports a failure to open its window.

Pyxel needs OpenGL, and when it cannot get it the Rust layer raises a
PanicException whose text means nothing to a player. That happens before any
game screen exists, so the in-game error screen cannot be used to report it:
these are the only thing standing between a player and a raw Rust traceback.
"""
# Requesting a fixture shadows the function that defines it; that is how
# pytest fixtures work, so the check is disabled for this file only.
# pylint: disable=redefined-outer-name
import logging
from typing import Any, List

import pytest

import bansoko.__main__ as game_main
from bansoko.__main__ import (GRAPHICS_ERROR_MESSAGE, initialize_display,
                              is_graphics_failure, report_startup_failure,
                              should_use_error_dialog)


@pytest.fixture(autouse=True)
def never_open_a_real_dialog(monkeypatch: pytest.MonkeyPatch) -> List[str]:
    """Replace the message box for every test in this module.

    A modal dialog on a machine with nobody to click it hangs until the job
    is killed, which is how a CI run was once lost. No amount of care in the
    logic under test is worth risking that again, so the real dialog is
    simply unreachable from here.
    """
    shown: List[str] = []
    monkeypatch.setattr(game_main, "show_error_dialog", shown.append)
    return shown


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


def test_no_dialog_when_running_from_source(never_open_a_real_dialog: List[str]) -> None:
    """A modal dialog must never appear where text would do.

    This is a regression test for a hung CI job. The dialog is only ever
    right for the frozen windowed build; running from source, as tests and CI
    do, it must never appear, because there is nobody to dismiss it.
    """
    report_startup_failure("something went wrong")

    assert not never_open_a_real_dialog, "a modal dialog was opened from source"
    assert not should_use_error_dialog(), "dialog wrongly considered necessary"


def test_dialog_is_used_in_a_frozen_windowed_build(
        monkeypatch: pytest.MonkeyPatch, never_open_a_real_dialog: List[str]) -> None:
    """The frozen windowed build has no stderr, so it gets the dialog."""
    monkeypatch.setattr(game_main, "should_use_error_dialog", lambda: True)

    report_startup_failure("something went wrong")

    assert never_open_a_real_dialog == ["something went wrong"]


def test_no_dialog_outside_a_frozen_build(monkeypatch: pytest.MonkeyPatch) -> None:
    """Only a frozen Windows build may use a dialog, whatever stderr does."""
    monkeypatch.setattr(game_main.sys, "platform", "win32")
    monkeypatch.setattr(game_main.sys, "stderr", None)
    monkeypatch.delattr(game_main.sys, "frozen", raising=False)
    assert not should_use_error_dialog()
