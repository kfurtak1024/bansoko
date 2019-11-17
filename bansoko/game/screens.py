import pyxel
from graphics.menu import Menu, MenuItem
from graphics.screen import Screen


class MainMenuScreen(Screen):
    def __init__(self):
        self.menu = Menu(
            self,
            [
                MenuItem("Start Game", lambda: GameScreen()),
                MenuItem("Choose Level", lambda: ChooseLevelScreen()),
                MenuItem("Exit", lambda: None)
            ])

    def update(self):
        return self.menu.update()

    def draw(self):
        pyxel.cls(1)
        pyxel.text(16, 16, "MAIN MENU", 7)
        self.menu.draw()


class GameScreen(Screen):
    def __init__(self):
        self.menu = Menu(
            self,
            [
                MenuItem("Pause Menu", lambda: GamePausedScreen()),
                MenuItem("Complete Level", lambda: LevelCompletedScreen())
            ])

    def update(self):
        return self.menu.update()

    def draw(self):
        pyxel.cls(1)
        pyxel.text(16, 16, "PLAYING GAME", 7)
        self.menu.draw()


class GamePausedScreen(Screen):
    def __init__(self):
        self.menu = Menu(
            self,
            [
                MenuItem("Resume Game", lambda: None),
                MenuItem("Restart Level", lambda: None),
                MenuItem("Back To Main Menu", lambda: MainMenuScreen())
            ])

    def update(self):
        return self.menu.update()

    def draw(self):
        pyxel.cls(1)
        pyxel.text(16, 16, "GAME PAUSED", 7)
        self.menu.draw()


class LevelCompletedScreen(Screen):
    def __init__(self):
        self.menu = Menu(
            self,
            [
                MenuItem("Play next level", lambda: GamePausedScreen()),
                MenuItem("Back To Main Menu", lambda: MainMenuScreen())
            ])

    def update(self):
        return self.menu.update()

    def draw(self):
        pyxel.cls(1)
        pyxel.text(16, 16, "LEVEL COMPLETE", 7)
        self.menu.draw()


class ChooseLevelScreen(Screen):
    def __init__(self):
        self.menu = Menu(
            self,
            [
                MenuItem("Start Level", lambda: GameScreen()),
                MenuItem("Back To Main Menu", lambda: None)
            ])

    def update(self):
        return self.menu.update()

    def draw(self):
        pyxel.cls(1)
        pyxel.text(16, 16, "CHOOSE LEVEL", 7)
        self.menu.draw()
