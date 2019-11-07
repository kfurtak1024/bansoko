import pyxel

from bansoko.game.screen import Screen, ScreenController


class MainMenuScreen(Screen):
    def update(self):
        if pyxel.btnp(pyxel.KEY_1):
            return GameScreen()
        if pyxel.btnp(pyxel.KEY_2):
            return ChooseLevelScreen()
        if pyxel.btnp(pyxel.KEY_3):
            return OptionsScreen()
        if pyxel.btnp(pyxel.KEY_4):
            return None
        return self

    def draw(self):
        pyxel.cls(0)
        pyxel.text(16, 16, "MAIN MENU\n=========\n1) Start Game\n2) Choose Level\n3) Options\n4) Exit", 1)


class GameScreen(Screen):
    def update(self):
        if pyxel.btnp(pyxel.KEY_1):
            return GamePausedScreen()
        return self

    def draw(self):
        pyxel.cls(0)
        pyxel.text(16, 16, "PLAYING GAME\n============\n1) Pause Menu", 2)


class GamePausedScreen(Screen):
    def update(self):
        if pyxel.btnp(pyxel.KEY_1):
            return None
        if pyxel.btnp(pyxel.KEY_2):
            return OptionsScreen()
        if pyxel.btnp(pyxel.KEY_3):
            return MainMenuScreen()
        return self

    def draw(self):
        pyxel.cls(0)
        pyxel.text(16, 16, "GAME PAUSED\n===========\n1) Continue Game\n2) Options\n3) Exit To Main Menu", 3)


class ChooseLevelScreen(Screen):
    def update(self):
        if pyxel.btnp(pyxel.KEY_1):
            return GameScreen()
        if pyxel.btnp(pyxel.KEY_2):
            return None
        return self

    def draw(self):
        pyxel.cls(0)
        pyxel.text(16, 16, "CHOOSE LEVEL\n============\n1) Start Level\n2) Exit To Main Menu", 4)


class OptionsScreen(Screen):
    def update(self):
        if pyxel.btnp(pyxel.KEY_1):
            return None
        return self

    def draw(self):
        pyxel.cls(0)
        pyxel.text(16, 16, "OPTIONS\n============\n1) Back", 4)


class App:
    def __init__(self):
        self.controller = ScreenController(MainMenuScreen(), self.__exit_callback)

    def run(self):
        pyxel.init(255, 255, caption="Bansoko", fps=60)
        pyxel.run(self.controller.update, self.controller.draw)

    @staticmethod
    def __exit_callback():
        pyxel.quit()