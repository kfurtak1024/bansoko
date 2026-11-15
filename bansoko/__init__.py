"""
 _|_|_|      _|_|    _|      _|    _|_|_|    _|_|    _|    _|    _|_|
 _|    _|  _|    _|  _|_|    _|  _|        _|    _|  _|  _|    _|    _|
 _|_|_|    _|_|_|_|  _|  _|  _|    _|_|    _|    _|  _|_|      _|    _|
 _|    _|  _|    _|  _|    _|_|        _|  _|    _|  _|  _|    _|    _|
 _|_|_|    _|    _|  _|      _|  _|_|_|      _|_|    _|    _|    _|_|

Main Bansoko module exposing game globals.
"""
__version__ = "2.0.0"

GAME_FRAME_RATE = 30
GAME_FRAME_TIME_IN_MS = 1_000 / GAME_FRAME_RATE

LEVEL_WIDTH = 32
LEVEL_HEIGHT = 32
LEVEL_NUM_LAYERS = 3
# Levels sit side by side in Pyxel's 256-tile-wide tilemap, and their
# thumbnails the same way in a 256-pixel-wide image bank.
LEVELS_PER_ROW = 256 // LEVEL_WIDTH
LEVEL_THUMBNAIL_IMAGE_BANK = 2
LEVEL_BASE_TILEMAP = 0

TILESET_IMAGE_BANK = 0
