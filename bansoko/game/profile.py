"""Module exposing PlayerProfile, that can read/write information about game progress."""
import os
from pathlib import Path
from typing import BinaryIO, Tuple

from bansoko.game.bundle import Bundle
from bansoko.game.level import LevelStatistics

GAME_PROFILE_LOCATION = ".bansoko"
GAME_PROFILE_FILE_NAME = "profile.data"

FILE_HEADER = bytes.fromhex("42 41 4E 53 01 00")
INITIALLY_UNLOCKED_LEVEL = 2
INT_SIZE_IN_BYTES = 4
LEVEL_STATS_SIZE_IN_BYTES = 3 * INT_SIZE_IN_BYTES


class PlayerProfile:
    def __init__(self, profile_file_path: Path, file_offset: int, last_unlocked_level: int,
                 levels_stats: Tuple[LevelStatistics, ...]):
        self._profile_file_path = profile_file_path
        self._file_offset = file_offset
        self._last_unlocked_level = last_unlocked_level
        self.levels_stats = levels_stats

    @property
    def last_unlocked_level(self) -> int:
        """The last unlocked level. The last level from all levels that can be played now."""
        return self._last_unlocked_level

    def is_level_unlocked(self, level_num: int) -> bool:
        """Test if specified level is unlocked (which means that it can be played now)

        :param level_num: level to be tested
        :return: true - if level is unlocked *OR* false - otherwise
        """
        return level_num <= self._last_unlocked_level

    def is_level_completed(self, level_num: int) -> bool:
        """Test if specified level was ever completed.

        :param level_num: level to be tested
        :return: true - if level was completed *OR* false - otherwise
        """
        return self.levels_stats[level_num].completed

    def complete_level(self, level_stats: LevelStatistics) -> None:
        """Save information about level completion to profile file. Additionally, as a reward,
        unlock next level.

        :param level_stats: statistics of level completion
        """
        if not self.is_level_completed(level_stats.level_num):
            self._last_unlocked_level = min(self._last_unlocked_level + 1,
                                            len(self.levels_stats) - 1)
        self.levels_stats[level_stats.level_num].merge_with(level_stats)

        with open(self._profile_file_path, "r+b") as profile_file:
            profile_file.seek(len(FILE_HEADER))
            _write_int(profile_file, self._last_unlocked_level)
            profile_file.seek(
                self._file_offset + level_stats.level_num * LEVEL_STATS_SIZE_IN_BYTES)
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


def __create_profile_file(profile_file_path: Path, bundle: Bundle) -> PlayerProfile:
    file_offset = len(FILE_HEADER) + INT_SIZE_IN_BYTES
    last_unlocked_level = INITIALLY_UNLOCKED_LEVEL
    levels_stats = tuple([LevelStatistics(level_num) for level_num in range(bundle.num_levels)])

    with open(profile_file_path, "wb") as profile_file:
        profile_file.write(FILE_HEADER)
        # TODO: Add bundle hashes (so multiple bundles can be supported)!!
        _write_int(profile_file, last_unlocked_level)
        _write_zeros(profile_file, bundle.num_levels * LEVEL_STATS_SIZE_IN_BYTES)

    return PlayerProfile(profile_file_path, file_offset, last_unlocked_level, levels_stats)


def __load_profile_file(profile_file_path: Path, bundle: Bundle) -> PlayerProfile:
    file_offset = len(FILE_HEADER) + INT_SIZE_IN_BYTES

    with open(profile_file_path, "rb") as profile_file:
        header = profile_file.read(len(FILE_HEADER))
        if header != FILE_HEADER:
            raise Exception(f"File '{profile_file_path}' is not a valid profile file")

        levels_stats = []

        # TODO: Read hash of a bundle from profile (so, we can save progress of different bundles)
        last_unlocked_level = _read_int(profile_file)
        for level_num in range(bundle.num_levels):
            level = LevelStatistics(level_num)
            level.steps = _read_int(profile_file)
            level.pushes = _read_int(profile_file)
            level.time_in_ms = _read_int(profile_file)
            levels_stats.append(level)

    return PlayerProfile(profile_file_path, file_offset, last_unlocked_level, tuple(levels_stats))


# TODO: Test it on Linux!


def _write_int(file: BinaryIO, value: int) -> None:
    file.write(value.to_bytes(INT_SIZE_IN_BYTES, byteorder="big"))


def _write_zeros(file: BinaryIO, count: int) -> None:
    file.write((0).to_bytes(count, byteorder="big"))


def _read_int(file: BinaryIO) -> int:
    return int.from_bytes(file.read(INT_SIZE_IN_BYTES), byteorder="big")
