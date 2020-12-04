"""Module exposing PlayerProfile, that can read/write information about game progress."""
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, List

from bansoko.game import GameError
from bansoko.game.bundle import Bundle, SHA1_SIZE_IN_BYTES

GAME_PROFILE_LOCATION = ".bansoko"
GAME_PROFILE_FILENAME = "profile.data"
GAME_LOG_FILENAME = "bansoko.log"

FILE_HEADER = bytes.fromhex("42 41 4E 53 01")
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

        total_seconds = self.time_in_ms // 1000
        total_minutes = total_seconds // 60
        total_hours = total_minutes // 60
        hours = total_hours % 60
        minutes = total_minutes % 60
        seconds = total_seconds % 60

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
            raise GameError("Cannot merge scores from different levels")

        if not self.completed:
            return level_score

        return LevelScore(
            level_num=self.level_num,
            completed=self.completed,
            pushes=min(self.pushes, level_score.pushes),
            steps=min(self.steps, level_score.steps),
            time_in_ms=min(self.time_in_ms, level_score.time_in_ms))


class PlayerProfile:
    """PlayerProfile is a storage for keeping player's game progress.

    Attributes:
        _profile_file_path - path of the player profile file
        _file_offset - position in profile file where level scores start (in bytes)
        _last_unlocked_level - index of last unlocked level
        levels_scores - list of scores for all levels
        last_played_level - last level played by player (not persisted)
    """

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

    @property
    def last_level(self) -> int:
        """The last level.."""
        return len(self.levels_scores) - 1

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

    def next_level_to_play(self, level_num: int) -> int:
        """Get the next level to be played after completion of given level."""
        if self._last_unlocked_level == self.last_level:
            return (level_num + 1) % (self.last_level + 1)

        future_levels = self.levels_scores[level_num + 1:self.last_unlocked_level + 1]
        next_level = next((level.level_num for level in future_levels if not level.completed),
                          self.first_not_completed_level)
        return next_level

    def complete_level(self, level_score: LevelScore) -> LevelScore:
        """Save information about level completion to profile file. Additionally, as a reward,
        unlock next level.

        :param level_score: score of level completion
        :return: the previous score for the completed level
        """
        logging.info("Updating player profile file with game progress")

        if not self.is_level_completed(level_score.level_num):
            level_to_be_unlocked = self._last_unlocked_level + 1
            if self._can_unlock_level(level_to_be_unlocked):
                self._last_unlocked_level = level_to_be_unlocked

        prev_level_score = self.levels_scores[level_score.level_num]
        new_level_score = prev_level_score.merge_with(level_score)
        self.levels_scores[level_score.level_num] = new_level_score

        try:
            with open(self._profile_file_path, "r+b") as profile_file:
                profile_file.seek(self._file_offset)
                _write_int(profile_file, self._last_unlocked_level)
                profile_file.seek(new_level_score.level_num * LEVEL_SCORE_SIZE_IN_BYTES, 1)
                _write_int(profile_file, 1 if new_level_score.completed else 0)
                _write_int(profile_file, new_level_score.steps)
                _write_int(profile_file, new_level_score.pushes)
                _write_int(profile_file, new_level_score.time_in_ms)
        except IOError as io_error:
            raise GameError(
                f"Unable to update player profile file '{self._profile_file_path}'. "
                "Progress lost :-(") from io_error

        return prev_level_score

    def _can_unlock_last_level(self) -> bool:
        return next(level.level_num for level in self.levels_scores if
                    not level.completed) == self.last_level

    def _can_unlock_level(self, level_to_be_unlocked: int) -> bool:
        if level_to_be_unlocked > self.last_level:
            return False

        return level_to_be_unlocked != self.last_level or self._can_unlock_last_level()


def create_or_load_profile(bundle: Bundle, profile_file_path: Path) -> PlayerProfile:
    """Create or load (if already exists) a player profile.

    :param bundle: bundle the profile should be initialized with
    :param profile_file_path: path to player profile file
    :return: initialized player profile
    """
    if not os.path.isfile(profile_file_path):
        return _create_profile_file(profile_file_path, bundle)

    return _load_profile_file(profile_file_path, bundle)


def _create_profile_file(profile_file_path: Path, bundle: Bundle) -> PlayerProfile:
    try:
        logging.info("Creating new player profile file '%s'", profile_file_path)
        with open(profile_file_path, "wb") as profile_file:
            profile_file.write(FILE_HEADER)
            return _init_player_profile(profile_file_path, profile_file, bundle)
    except IOError as io_error:
        raise GameError("Unable to create player profile file") from io_error


def _load_profile_file(profile_file_path: Path, bundle: Bundle) -> PlayerProfile:
    try:
        logging.info("Loading existing player profile file '%s'", profile_file_path)
        with open(profile_file_path, "r+b") as profile_file:
            header = profile_file.read(len(FILE_HEADER))
            if header != FILE_HEADER:
                raise GameError("File is not a valid player profile file")

            while True:
                sha1 = profile_file.read(SHA1_SIZE_IN_BYTES)
                if not sha1:
                    break

                section_size = _read_int(profile_file)

                if sha1 == bundle.sha1:
                    return _read_player_profile(profile_file_path, profile_file, bundle)

                profile_file.seek(section_size, 1)

            return _init_player_profile(profile_file_path, profile_file, bundle)
    except IOError as io_error:
        raise GameError("Unable to open player profile file") from io_error
    except EOFError as eof_error:
        raise GameError("Unexpected end of player profile file") from eof_error


def _write_int(file: BinaryIO, value: int) -> None:
    file.write(value.to_bytes(INT_SIZE_IN_BYTES, byteorder="big"))


def _write_zeros(file: BinaryIO, count: int) -> None:
    file.write((0).to_bytes(count, byteorder="big"))


def _init_player_profile(profile_file_path: Path, profile_file: BinaryIO,
                         bundle: Bundle) -> PlayerProfile:
    profile_file.write(bundle.sha1)
    _write_int(profile_file, INT_SIZE_IN_BYTES + bundle.num_levels * LEVEL_SCORE_SIZE_IN_BYTES)

    file_offset = profile_file.tell()
    last_unlocked_level = INITIALLY_UNLOCKED_LEVEL
    levels_scores = [LevelScore(level_num) for level_num in range(bundle.num_levels)]

    _write_int(profile_file, last_unlocked_level)
    _write_zeros(profile_file, bundle.num_levels * LEVEL_SCORE_SIZE_IN_BYTES)

    return PlayerProfile(profile_file_path, file_offset, last_unlocked_level, levels_scores)


def _read_int(file: BinaryIO) -> int:
    int_from_file = file.read(INT_SIZE_IN_BYTES)
    if len(int_from_file) != INT_SIZE_IN_BYTES:
        raise EOFError()
    return int.from_bytes(int_from_file, byteorder="big")


def _read_player_profile(profile_file_path: Path, profile_file: BinaryIO,
                         bundle: Bundle) -> PlayerProfile:
    levels_scores = []
    file_offset = profile_file.tell()
    last_unlocked_level = _read_int(profile_file)
    for level_num in range(bundle.num_levels):
        levels_scores.append(
            LevelScore(
                level_num=level_num,
                completed=_read_int(profile_file) > 0,
                steps=_read_int(profile_file),
                pushes=_read_int(profile_file),
                time_in_ms=_read_int(profile_file)))

    return PlayerProfile(profile_file_path, file_offset, last_unlocked_level,
                         levels_scores)
