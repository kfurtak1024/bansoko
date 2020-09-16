import os
from pathlib import Path
from typing import List, Optional, BinaryIO

from bansoko import GAME_PROFILE_LOCATION, GAME_PROFILE_FILE_NAME
from bansoko.game.bundle import Bundle
from bansoko.game.level import LevelStatistics


# TODO: This whole module needs to be refactored!


class PlayerProfile:
    def __init__(self, profile_file_path: Path, file_offset: int, last_unlocked_level: int,
                 level_stats: List[Optional[LevelStatistics]]) -> None:
        self.profile_file_path = profile_file_path
        self.file_offset = file_offset
        self.last_unlocked_level = last_unlocked_level
        self.level_stats = level_stats

    def is_level_unlocked(self, level_num: int) -> bool:
        return level_num <= self.last_unlocked_level

    def is_level_completed(self, level_num: int) -> bool:
        return self.level_stats[level_num] is not None

    def complete_level(self, level_stats: LevelStatistics) -> None:
        if not self.is_level_completed(level_stats.level_num):
            self.last_unlocked_level = min(self.last_unlocked_level + 1, len(self.level_stats) - 1)
        # TODO: Overwrite only statistics which break high score
        self.level_stats[level_stats.level_num] = level_stats

        with open(self.profile_file_path, "r+b") as profile_file:
            profile_file.seek(len(FILE_HEADER))
            _write_int(profile_file, self.last_unlocked_level)
            profile_file.seek(self.file_offset + level_stats.level_num * 3 * 4)
            _write_int(profile_file, level_stats.steps)
            _write_int(profile_file, level_stats.pushes)
            _write_int(profile_file, level_stats.time_in_ms)


def create_or_load_profile(bundle: Bundle) -> PlayerProfile:
    profile_dir = Path.home().joinpath(GAME_PROFILE_LOCATION)
    os.makedirs(profile_dir, exist_ok=True)
    profile_file_path = profile_dir.joinpath(GAME_PROFILE_FILE_NAME)
    if not os.path.isfile(profile_file_path):
        return __create_profile_file(profile_file_path, bundle)

    return __load_profile_file(profile_file_path, bundle)


FILE_HEADER = bytes.fromhex("42 41 4E 53 01 00")


def __create_profile_file(profile_file_path: Path, bundle: Bundle) -> PlayerProfile:
    file_offset = len(FILE_HEADER) + 4
    last_unlocked_level = 2
    level_stats: List[Optional[LevelStatistics]] = [None] * bundle.num_levels

    with open(profile_file_path, "wb") as profile_file:
        profile_file.write(FILE_HEADER)
        # TODO: Add bundle hashes (so multiple bundles can be supported)!!
        _write_int(profile_file, last_unlocked_level)
        profile_file.write((0).to_bytes(bundle.num_levels * 3 * 4, byteorder="big"))

    return PlayerProfile(profile_file_path, file_offset, last_unlocked_level, level_stats)


def __load_profile_file(profile_file_path: Path, bundle: Bundle) -> PlayerProfile:
    file_offset = len(FILE_HEADER) + 4

    with open(profile_file_path, "rb") as profile_file:
        header = profile_file.read(len(FILE_HEADER))
        if header != FILE_HEADER:
            raise Exception(f"File '{profile_file_path}' is not a valid profile file")

        level_stats = []

        # TODO: Read hash of a bundle from profile (so, we can save progress of different bundles)
        last_unlocked_level = _read_int(profile_file)
        for level_num in range(bundle.num_levels):
            level = LevelStatistics(level_num)
            level.steps = _read_int(profile_file)
            level.pushes = _read_int(profile_file)
            level.time_in_ms = _read_int(profile_file)
            level_stats.append(level if level.time_in_ms > 0 else None)

    return PlayerProfile(profile_file_path, file_offset, last_unlocked_level, level_stats)


def _write_int(file: BinaryIO, value: int) -> None:
    # TODO: Make it os independent
    file.write(value.to_bytes(4, byteorder="big"))


def _read_int(file: BinaryIO) -> int:
    # TODO: Make it os independent
    return int.from_bytes(file.read(4), byteorder="big")
