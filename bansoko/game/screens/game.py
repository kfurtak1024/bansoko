import pyxel

from graphics.menu import Menu, MenuItem
from graphics.screen import Screen
from . import game_paused
from . import level_completed


class GameScreen(Screen):
    def __init__(self):
        self.menu = Menu(
            self,
            [
                MenuItem("[DEV] Pause Menu", lambda: game_paused.GamePausedScreen()),
                MenuItem("[DEV] Complete Level", lambda: level_completed.LevelCompletedScreen())
            ])

    def update(self):
        return self.menu.update()

    def draw(self):
        pyxel.cls(1)
        pyxel.text(16, 16, "PLAYING GAME", 7)
        self.menu.draw()
