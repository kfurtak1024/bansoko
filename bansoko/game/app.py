import pyxel


class App:
    def __init__(self):
        pyxel.init(256, 255)

    def run(self):
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    def draw(self):
        pyxel.cls(0)
        pyxel.rect(10, 10, 20, 20, 11)
