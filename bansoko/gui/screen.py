"""
Module for game screens management.
"""
import abc


class Screen(abc.ABC):
    """
    Base class for all game screens that suppose to be managed by ScreenController.
    Screens are updated and drawn once per frame. Screen transitions are triggered by
    values returned in update method.
    """

    def activate(self) -> None:
        pass

    @abc.abstractmethod
    def update(self):
        """
        Update screen state. Control screen transitions by return value.
        Called once per frame (only if screen is on top of screen stack)

        Returns:
            - self (or any instance of type(self)) - no screen transition
            - instance of Screen class - switch to new screen
            - None - switch to previous screen (perform pop on screen stack)
        """

    @abc.abstractmethod
    def draw(self) -> None:
        """
        Draw screen.
        Called once per frame (only if screen is on top of screen stack)
        """

    def __eq__(self, other):
        return isinstance(self, type(other))


class ScreenController:
    def __init__(self, start_screen: Screen, exit_callback=None):
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

    def __switch_to_screen(self, new_screen: Screen) -> None:
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
