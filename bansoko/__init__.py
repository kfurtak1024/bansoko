"""
 _|_|_|      _|_|    _|      _|    _|_|_|    _|_|    _|    _|    _|_|
 _|    _|  _|    _|  _|_|    _|  _|        _|    _|  _|  _|    _|    _|
 _|_|_|    _|_|_|_|  _|  _|  _|    _|_|    _|    _|  _|_|      _|    _|
 _|    _|  _|    _|  _|    _|_|        _|  _|    _|  _|  _|    _|    _|
 _|_|_|    _|    _|  _|      _|  _|_|_|      _|_|    _|    _|    _|_|

Main Bansoko module exposing game globals.
"""
__version__ = "0.9.0"

GAME_FRAME_RATE = 30
GAME_FRAME_TIME_IN_MS = 1_000 / GAME_FRAME_RATE

LEVEL_WIDTH = 32
LEVEL_HEIGHT = 32
LEVEL_NUM_LAYERS = 3
LEVEL_THUMBNAIL_IMAGE_BANK = 2

TILEMAP_WIDTH = 256
TILEMAP_HEIGHT = 256
TILE_SIZE = 8

SPRITE_IMAGE_BANK = 1

IMAGE_BANK_WIDTH = 256
IMAGE_BANK_HEIGHT = 256
