"""Module exposing PlayerProfile, that can read/write information about game progress."""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, List

from bansoko.game.bundle import Bundle

GAME_PROFILE_LOCATION = ".bansoko"
GAME_PROFILE_FILE_NAME = "profile.data"

FILE_HEADER = bytes.fromhex("42 41 4E 53 01 00")
INITIALLY_UNLOCKED_LEVEL = 2
INT_SIZE_IN_BYTES = 4
LEVEL_SCORE_SIZE_IN_BYTES = 4 * INT_SIZE_IN_BYTES


@dataclass(frozen=True)
class LevelScore:
    """Player's score for given level.

    Attributes:
        level_num - level number
        completed - has level been completed
        pushes - number of moves that player made ("move" happens when player pushes a crate)
        steps - number of steps that player made ("step" happens when player moves by one cell in
                any direction)
        time_in_ms - time spent playing the level (expressed in milliseconds)
    """
    level_num: int
    completed: bool = False
    pushes: int = 0
    steps: int = 0
    time_in_ms: int = 0

    @property
    def time(self) -> str:
        """Human readable level completion time expressed in format H:MM:SS."""
        # TODO: Refactor this
        hours = int((self.time_in_ms / (1000 * 60 * 60)) % 60)
        minutes = int((self.time_in_ms / (1000 * 60)) % 60)
        seconds = int((self.time_in_ms / 1000) % 60)
        if self.time_in_ms >= 10 * 60 * 60 * 1000:
            hours = 9
            seconds = 59
            minutes = 59

        return "{:d}:{:02d}:{:02d}".format(hours, minutes, seconds)

    def merge_with(self, level_score: "LevelScore") -> "LevelScore":
        """Merge this level score with given score.

        In case of differences in field values prefer better score
        (smaller number of steps, pushes, quicker completion time)

        :param level_score: level score to merge with
        :return: newly created level score which is a result of merge
        """
        if self == level_score:
            return level_score
        if self.level_num != level_score.level_num:
            raise Exception("Cannot merge scores from different levels")

        if not self.completed:
            return level_score

        return LevelScore(
            level_num=self.level_num,
            completed=self.completed,
            pushes=min(self.pushes, level_score.pushes),
            steps=min(self.steps, level_score.steps),
            time_in_ms=min(self.time_in_ms, level_score.time_in_ms))


class PlayerProfile:
    def __init__(self, profile_file_path: Path, file_offset: int, last_unlocked_level: int,
                 levels_scores: List[LevelScore]):
        self._profile_file_path = profile_file_path
        self._file_offset = file_offset
        self._last_unlocked_level = last_unlocked_level
        self.levels_scores = levels_scores
        self.last_played_level = 0

    @property
    def first_not_completed_level(self) -> int:
        """The first not completed level.

        This is the level that is going to be started when player chooses 'START GAME' option in
        main menu.

        :return: The first not completed level if there is one *OR* 0 otherwise
        """
        level = next((level for level in self.levels_scores if not level.completed),
                     self.levels_scores[0])
        return level.level_num

    @property
    def last_unlocked_level(self) -> int:
        """The last unlocked level. The last level from all levels that can be played now."""
        return self._last_unlocked_level

    def is_level_unlocked(self, level_num: int) -> bool:
        """Test if specified level is unlocked (which means that it can be played now)

        :param level_num: level to be tested
        :return: True - if level is unlocked *OR* False - otherwise
        """
        return level_num <= self._last_unlocked_level

    def is_level_completed(self, level_num: int) -> bool:
        """Test if specified level was ever completed.

        :param level_num: level to be tested
        :return: True - if level was completed *OR* False - otherwise
        """
        return self.levels_scores[level_num].completed

    def complete_level(self, level_score: LevelScore) -> LevelScore:
        """Save information about level completion to profile file. Additionally, as a reward,
        unlock next level.

        :param level_score: score of level completion
        :return: the previous score for the completed level
        """
        if not self.is_level_completed(level_score.level_num):
            self._last_unlocked_level = min(self._last_unlocked_level + 1,
                                            len(self.levels_scores) - 1)

        prev_level_score = self.levels_scores[level_score.level_num]
        new_level_score = prev_level_score.merge_with(level_score)
        self.levels_scores[level_score.level_num] = new_level_score

        with open(self._profile_file_path, "r+b") as profile_file:
            profile_file.seek(len(FILE_HEADER))
            _write_int(profile_file, self._last_unlocked_level)
            profile_file.seek(
                self._file_offset + new_level_score.level_num * LEVEL_SCORE_SIZE_IN_BYTES)
            _write_int(profile_file, 1 if new_level_score.completed else 0)
            _write_int(profile_file, new_level_score.steps)
            _write_int(profile_file, new_level_score.pushes)
            _write_int(profile_file, new_level_score.time_in_ms)

        return prev_level_score


def create_or_load_profile(bundle: Bundle) -> PlayerProfile:
    """Create or load (if already exists) a player profile.

    :param bundle: bundle the profile should be initialized with
    :return: initialized player profile
    """
    profile_dir = Path.home().joinpath(GAME_PROFILE_LOCATION)
    os.makedirs(profile_dir, exist_ok=True)
    profile_file_path = profile_dir.joinpath(GAME_PROFILE_FILE_NAME)
    if not os.path.isfile(profile_file_path):
        return __create_profile_file(profile_file_path, bundle)

    return __load_profile_file(profile_file_path, bundle)


def __create_profile_file(profile_file_path: Path, bundle: Bundle) -> PlayerProfile:
    file_offset = len(FILE_HEADER) + INT_SIZE_IN_BYTES
    last_unlocked_level = INITIALLY_UNLOCKED_LEVEL
    levels_scores = [LevelScore(level_num) for level_num in range(bundle.num_levels)]

    with open(profile_file_path, "wb") as profile_file:
        profile_file.write(FILE_HEADER)
        # TODO: Add bundle hashes (so multiple bundles can be supported)!!
        _write_int(profile_file, last_unlocked_level)
        _write_zeros(profile_file, bundle.num_levels * LEVEL_SCORE_SIZE_IN_BYTES)

    return PlayerProfile(profile_file_path, file_offset, last_unlocked_level, levels_scores)


def __load_profile_file(profile_file_path: Path, bundle: Bundle) -> PlayerProfile:
    file_offset = len(FILE_HEADER) + INT_SIZE_IN_BYTES

    with open(profile_file_path, "rb") as profile_file:
        header = profile_file.read(len(FILE_HEADER))
        if header != FILE_HEADER:
            raise Exception(f"File '{profile_file_path}' is not a valid profile file")

        levels_scores = []

        # TODO: Read hash of a bundle from profile (so, we can save progress of different bundles)
        last_unlocked_level = _read_int(profile_file)
        for level_num in range(bundle.num_levels):
            levels_scores.append(
                LevelScore(
                    level_num=level_num,
                    completed=_read_int(profile_file) > 0,
                    steps=_read_int(profile_file),
                    pushes=_read_int(profile_file),
                    time_in_ms=_read_int(profile_file)))

    return PlayerProfile(profile_file_path, file_offset, last_unlocked_level, levels_scores)


# TODO: Test it on Linux!


def _write_int(file: BinaryIO, value: int) -> None:
    file.write(value.to_bytes(INT_SIZE_IN_BYTES, byteorder="big"))


def _write_zeros(file: BinaryIO, count: int) -> None:
    file.write((0).to_bytes(count, byteorder="big"))


def _read_int(file: BinaryIO) -> int:
    return int.from_bytes(file.read(INT_SIZE_IN_BYTES), byteorder="big")
