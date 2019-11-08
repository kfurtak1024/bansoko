import abc


class Screen(abc.ABC):
    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def draw(self):
        pass

    def __eq__(self, other):
        return isinstance(self, type(other))


class ScreenController:
    def __init__(self, start_screen: Screen, exit_callback=None):
        self.screen_stack = [start_screen]
        self.skip_next_draw = False
        self.exit_callback = exit_callback

    def update(self):
        if self.screen_stack:
            new_screen = self.screen_stack[-1].update()
            if new_screen is not self.screen_stack[-1]:
                self.__switch_to_screen(new_screen)
        else:
            self.exit_callback()
            self.skip_next_draw = True

    def draw(self):
        if not self.skip_next_draw:
            self.screen_stack[-1].draw()
        self.skip_next_draw = False

    def __switch_to_screen(self, new_screen: Screen):
        if new_screen is None:
            self.screen_stack.pop()
        else:
            self.__unwind_screen_stack(new_screen)
            self.screen_stack.append(new_screen)
        self.skip_next_draw = True

    def __unwind_screen_stack(self, screen):
        try:
            del self.screen_stack[self.screen_stack.index(screen):]
        except ValueError:
            pass
