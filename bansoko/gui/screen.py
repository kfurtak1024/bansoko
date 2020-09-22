"""Module for game screens management."""
from typing import Optional, Callable, Any

from bansoko.graphics.background import Background
from bansoko.gui.input import InputSystem


class Screen:
    """Base class for all game screens that suppose to be managed by ScreenController.

    Screens are updated and drawn once per frame. Screen transitions are triggered by
    values returned in update method.
    """

    def __init__(self, background: Optional[Background] = None):
        self.background = background
        self.input = InputSystem()

    def activate(self) -> None:
        """Called each time Screen is put on top of screen stack by ScreenController."""
        self.input.reset()

    def update(self) -> Optional["Screen"]:
        """Update screen state. Control screen transitions by return value.

        Called once per frame (only if screen is on top of screen stack)

        :return: self (or any instance of type(self)) - no screen transition *OR*
        instance of Screen class - switch to new screen *OR* None - switch to previous screen
        (perform pop on screen stack)
        """
        self.input.update()
        return self

    def draw(self) -> None:
        """Draw screen.

        Called once per frame (only if screen is on top of screen stack)
        """
        if self.background is not None:
            self.background.draw()

    def __eq__(self, other: Any) -> bool:
        return isinstance(self, type(other))


class ScreenController:
    """ScreenController manages game screens.

    Game screens are organized in a stack. Screen from the top is called an active Screen.
    Active screen receives update and draw calls once per frame.
    Active screen can trigger:
        - switch to new screen (which will be put on top of the stack and activated)
        - end its life and switch to previous screen (screen from top will be popped from the stack
          and then new screen from top will be activated)
    Switching between screens is controlled by update() callback from Screen class.
    """

    def __init__(self, start_screen: Screen, exit_callback: Callable[[], None]):
        self.screen_stack = [start_screen]
        self.exit_callback = exit_callback
        self.skip_next_draw = False
        start_screen.activate()

    def update(self) -> None:
        """Update screen from top of screen stack. Manage screen transitions."""
        if self.screen_stack:
            new_screen = self.screen_stack[-1].update()
            if new_screen is not self.screen_stack[-1]:
                self.__switch_to_screen(new_screen)
        else:
            self.exit_callback()
            self.skip_next_draw = True

    def draw(self) -> None:
        """Draw screen from top of screen stack."""
        if not self.skip_next_draw:
            self.screen_stack[-1].draw()
        self.skip_next_draw = False

    def __switch_to_screen(self, new_screen: Optional[Screen]) -> None:
        if new_screen is None:
            self.screen_stack.pop()
        else:
            self.__unwind_screen_stack(new_screen)
            self.screen_stack.append(new_screen)
        if self.screen_stack:
            self.screen_stack[-1].activate()
        self.skip_next_draw = True

    def __unwind_screen_stack(self, screen: Screen) -> None:
        try:
            del self.screen_stack[self.screen_stack.index(screen):]
        except ValueError:
            pass
