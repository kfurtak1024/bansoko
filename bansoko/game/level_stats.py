from typing import NamedTuple


class LevelStats(NamedTuple):
    level: int
    moves: int = 0
    steps: int = 0
    time: int = 0
