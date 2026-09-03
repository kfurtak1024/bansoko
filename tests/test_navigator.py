"""Tests for screen navigation, in particular how the game decides to quit.

When the last screen pops itself the navigator calls its exit callback and the
window disappears. That is indistinguishable from a crash to anyone watching,
so the path is worth pinning down: it is how a game that "just closes" behaves
when nothing has actually gone wrong.
"""
from typing import List, Optional

from bansoko.gui.navigator import ScreenController, ScreenNavigator

FRAME_MS = 1000 / 30


class FakeScreen(ScreenController):
    """A screen that returns whatever it is told to."""

    def __init__(self, returns: Optional[ScreenController] = None,
                 pop_self: bool = False) -> None:
        super().__init__()
        self.returns = returns
        self.pop_self = pop_self
        self.activated = 0

    def activate(self) -> None:
        self.activated += 1

    def update(self, dt_in_ms: float) -> Optional[ScreenController]:
        del dt_in_ms
        if self.pop_self:
            return None
        return self.returns if self.returns is not None else self

    def draw(self, draw_as_secondary: bool = False) -> None:
        del draw_as_secondary


def test_start_screen_is_activated() -> None:
    """The first screen is activated when navigation begins."""
    screen = FakeScreen()
    ScreenNavigator(screen, lambda: None, FRAME_MS)
    assert screen.activated == 1


def test_staying_on_a_screen_does_not_exit() -> None:
    """A screen returning itself keeps the game running."""
    exits: List[bool] = []
    navigator = ScreenNavigator(FakeScreen(), lambda: exits.append(True), FRAME_MS)

    for _ in range(5):
        navigator.update()

    assert not exits


def test_popping_the_last_screen_exits_the_game() -> None:
    """Once the last screen pops itself, the exit callback runs.

    This is the quiet path: no error, no log of its own before this was
    added, just a window that closes.
    """
    exits: List[bool] = []
    navigator = ScreenNavigator(FakeScreen(pop_self=True),
                                lambda: exits.append(True), FRAME_MS)

    navigator.update()   # the screen pops itself
    assert not exits, "should not exit while a screen is still on the stack"

    navigator.update()   # stack is empty now
    assert exits == [True]


class AnotherFakeScreen(ScreenController):
    """A screen of an unrelated type.

    The navigator decides whether to switch with isinstance(new, type(current)),
    so screens are told apart by type, and that check follows inheritance: a
    subclass of the current screen would not count as a different screen. This
    is deliberately a sibling of FakeScreen, not a child of it.
    """

    def __init__(self) -> None:
        super().__init__()
        self.activated = 0

    def activate(self) -> None:
        self.activated += 1

    def update(self, dt_in_ms: float) -> Optional[ScreenController]:
        del dt_in_ms
        return self

    def draw(self, draw_as_secondary: bool = False) -> None:
        del draw_as_secondary


def test_switching_screens_activates_the_new_one() -> None:
    """Navigating to another screen activates it and keeps the game running."""
    exits: List[bool] = []
    destination = AnotherFakeScreen()
    navigator = ScreenNavigator(FakeScreen(returns=destination),
                                lambda: exits.append(True), FRAME_MS)

    navigator.update()

    assert destination.activated == 1
    assert not exits
