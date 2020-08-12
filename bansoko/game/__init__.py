import pyxel

GAME_RESOURCE_FILE = "../gamedata/main.pyxres"


def load_bundle(bundle_name: str):
    # TODO: bundle_name is not used!
    pyxel.load(GAME_RESOURCE_FILE)
    # TODO: Loading metadata file
