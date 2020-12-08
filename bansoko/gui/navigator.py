"""Module for game screens management."""
import abc
from typing import Optional, Callable, List

from bansoko.gui.input import InputSystem
from bansoko.gui.screen import Screen


class ScreenController(abc.ABC):
    """Base class for all game screen controllers that suppose to be managed by ScreenNavigator.

    Screen controllers are updated and drawn once per frame. Screen transitions are triggered by
    values returned in update method.
    """

    def __init__(self, semi_transparent: Optional[bool] = False) -> None:
        self.semi_transparent = semi_transparent

    @abc.abstractmethod
    def activate(self) -> None:
        """Called each time screen controller is put on top of screen stack by ScreenNavigator."""

    @abc.abstractmethod
    def update(self, dt_in_ms: float) -> Optional["ScreenController"]:
        """Update screen controller state. Control screen transitions by returning value.

        Called once per frame (only if screen is on top of screen stack)

        :param dt_in_ms: delta time since last update (in ms)
        :return: self (or any instance of type(self)) - no screen transition *OR*
        instance of ScreenController class - switch to new screen controller *OR*
        None - switch to previous screen controller (perform pop on screen stack)
        """

    @abc.abstractmethod
    def draw(self, draw_as_secondary: bool = False) -> None:
        """Draw screen.

        Called once per frame (only if screen controller is on top of screen stack)

        :param draw_as_secondary: is this screen drawn as a secondary (background) screen
        """


class BaseScreenController(ScreenController):
    """Base class for all game screen controllers that suppose to be managed by ScreenNavigator.

    Screen controllers are updated and drawn once per frame. Screen transitions are triggered by
    values returned in update method.
    """

    def __init__(self, semi_transparent: Optional[bool] = False,
                 screen: Optional[Screen] = None) -> None:
        super().__init__(semi_transparent)
        self.screen = screen
        self.input = InputSystem()

    def activate(self) -> None:
        self.input.reset()

    def update(self, dt_in_ms: float) -> Optional["ScreenController"]:
        self.input.update()
        return self

    def draw(self, draw_as_secondary: bool = False) -> None:
        if self.screen is not None:
            self.screen.draw()


class ScreenNavigator:
    """ScreenNavigator manages game screen controllers.

    Game screen controllers are organized in a stack. Screen controller from the top is called an
    active screen controller. Active screen controller receives update and draw calls once per
    frame.
    Active screen controller can trigger:
        - switch to new screen controller (which will be put on top of the stack and activated)
        - end its life and switch to previous screen controller (controller from top will be popped
          from the stack and then new controller from top will be activated)
    Switching between screen controllers is controlled by update() callback from ScreenController
    class.
    """

    def __init__(self, start_controller: ScreenController, exit_callback: Callable[[], None],
                 frame_time: float):
        self.controllers_stack = [start_controller]
        self.exit_callback = exit_callback
        self.frame_time = frame_time
        self.skip_next_draw = False
        start_controller.activate()

    def update(self) -> None:
        """Update screen controller from top of controllers stack. Manage screen transitions."""
        if self.controllers_stack:
            new_screen = self.controllers_stack[-1].update(self.frame_time)
            if not isinstance(new_screen, type(self.controllers_stack[-1])):
                self._switch_to_screen(new_screen)
        else:
            self.exit_callback()
            self.skip_next_draw = True

    def draw(self) -> None:
        """Draw screen controller from top of controllers stack."""
        if not self.skip_next_draw:
            screens_to_be_drawn: List[ScreenController] = []
            for screen in reversed(self.controllers_stack):
                screens_to_be_drawn.insert(0, screen)
                if not screen.semi_transparent:
                    break

            for (i, screen) in enumerate(screens_to_be_drawn):
                is_top_screen = (i == len(screens_to_be_drawn) - 1)
                screen.draw(draw_as_secondary=not is_top_screen)
        self.skip_next_draw = False

    def _switch_to_screen(self, new_screen: Optional[ScreenController]) -> None:
        if new_screen is None:
            self.controllers_stack.pop()
        else:
            self._unwind_screen_stack(new_screen)
            self.controllers_stack.append(new_screen)
        if self.controllers_stack:
            self.controllers_stack[-1].activate()
        self.skip_next_draw = True

    def _unwind_screen_stack(self, screen_to_unwind_to: ScreenController) -> None:
        for i, screen in enumerate(self.controllers_stack):
            if isinstance(screen, type(screen_to_unwind_to)):
                del self.controllers_stack[i:]
                break
