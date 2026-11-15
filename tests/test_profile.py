"""Tests for the player profile format.

The profile file is the only piece of persistent player state, and it is
keyed by the bundle SHA1. These tests pin down the behaviour that protects
existing progress across releases.
"""
import dataclasses
from pathlib import Path

from bansoko.game.bundle import Bundle
from bansoko.game.profile import (FILE_HEADER, INITIALLY_UNLOCKED_LEVEL, INT_SIZE_IN_BYTES,
                                  LEVEL_SCORE_SIZE_IN_BYTES, LevelScore, PlayerProfile,
                                  create_or_load_profile)


def test_new_profile_starts_with_initial_levels_unlocked(bundle: Bundle,
                                                        tmp_path: Path) -> None:
    """A fresh profile unlocks the opening levels and records no progress."""
    profile = create_or_load_profile(bundle, tmp_path / "profile.data")
    assert profile.last_unlocked_level == INITIALLY_UNLOCKED_LEVEL
    assert profile.is_level_unlocked(INITIALLY_UNLOCKED_LEVEL)
    assert not profile.is_level_unlocked(INITIALLY_UNLOCKED_LEVEL + 1)
    assert not any(score.completed for score in profile.levels_scores)


def test_new_profile_writes_expected_header(bundle: Bundle, tmp_path: Path) -> None:
    """The magic header identifies the file as a Bansoko profile."""
    path = tmp_path / "profile.data"
    create_or_load_profile(bundle, path)
    assert path.read_bytes()[:len(FILE_HEADER)] == FILE_HEADER


def test_progress_survives_a_reload(bundle: Bundle, tmp_path: Path) -> None:
    """Completing a level persists its score and unlocks the next one."""
    path = tmp_path / "profile.data"

    profile = create_or_load_profile(bundle, path)
    profile.complete_level(LevelScore(level_num=0, completed=True, pushes=10, steps=20,
                                      time_in_ms=1234))

    reloaded = create_or_load_profile(bundle, path)
    score = reloaded.levels_scores[0]
    assert score.completed
    assert (score.pushes, score.steps, score.time_in_ms) == (10, 20, 1234)
    assert reloaded.last_unlocked_level == INITIALLY_UNLOCKED_LEVEL + 1


def test_progress_for_another_bundle_is_preserved(bundle: Bundle, tmp_path: Path) -> None:
    """Loading a different bundle must append a section, not overwrite one.

    A player who installs a mod and then goes back to the base game keeps
    their progress in both.
    """
    path = tmp_path / "profile.data"
    original = bundle
    modded = dataclasses.replace(original, sha1=bytearray(b"f" * 40))

    profile = create_or_load_profile(original, path)
    profile.complete_level(LevelScore(level_num=0, completed=True, pushes=1, steps=2,
                                      time_in_ms=3))

    mod_profile = create_or_load_profile(modded, path)
    assert not mod_profile.levels_scores[0].completed

    back_to_original = create_or_load_profile(original, path)
    assert back_to_original.levels_scores[0].completed
    assert back_to_original.levels_scores[0].pushes == 1


def test_merge_keeps_the_better_score() -> None:
    """Merging two completed scores keeps the best of each statistic."""
    best = LevelScore(level_num=1, completed=True, pushes=5, steps=10, time_in_ms=100)
    worse = LevelScore(level_num=1, completed=True, pushes=9, steps=20, time_in_ms=500)
    merged = best.merge_with(worse)
    assert (merged.pushes, merged.steps, merged.time_in_ms) == (5, 10, 100)


def test_merge_with_an_uncompleted_score_takes_the_new_one() -> None:
    """A never-played level takes whatever score arrives."""
    never_played = LevelScore(level_num=1)
    played = LevelScore(level_num=1, completed=True, pushes=5, steps=10, time_in_ms=100)
    assert never_played.merge_with(played) == played


def test_level_score_time_formatting() -> None:
    """Completion time renders as H:MM:SS and clamps at ten hours."""
    assert LevelScore(level_num=0, time_in_ms=0).time == "0:00:00"
    assert LevelScore(level_num=0, time_in_ms=61_000).time == "0:01:01"
    assert LevelScore(level_num=0, time_in_ms=3_661_000).time == "1:01:01"
    # Anything at or beyond ten hours is clamped to the display maximum.
    assert LevelScore(level_num=0, time_in_ms=10 * 60 * 60 * 1000).time == "9:59:59"


def _complete(profile: PlayerProfile, level_num: int) -> None:
    profile.complete_level(LevelScore(level_num=level_num, completed=True, pushes=1, steps=1,
                                      time_in_ms=1))


def test_the_last_level_unlocks_when_every_other_level_is_completed(bundle: Bundle,
                                                                    tmp_path: Path) -> None:
    """Finishing the level before last opens the last one, and not a level sooner."""
    profile = create_or_load_profile(bundle, tmp_path / "profile.data")
    last_level = profile.last_level

    for level_num in range(last_level - 1):
        _complete(profile, level_num)
    assert not profile.is_level_unlocked(last_level)

    _complete(profile, last_level - 1)
    assert profile.is_level_unlocked(last_level)


def test_the_last_level_stays_locked_while_an_earlier_one_is_open(bundle: Bundle,
                                                                  tmp_path: Path) -> None:
    """Skipping a level keeps the last one locked until the player goes back for it."""
    profile = create_or_load_profile(bundle, tmp_path / "profile.data")
    last_level = profile.last_level

    for level_num in range(1, last_level):
        _complete(profile, level_num)
    assert not profile.is_level_unlocked(last_level)

    _complete(profile, 0)
    assert profile.is_level_unlocked(last_level)


def test_a_profile_saved_with_the_last_level_wrongly_locked_opens_it(bundle: Bundle,
                                                                     tmp_path: Path) -> None:
    """Older versions never unlocked the last level; such a profile is put right on load."""
    path = tmp_path / "profile.data"
    profile = create_or_load_profile(bundle, path)
    last_level = profile.last_level
    for level_num in range(last_level):
        _complete(profile, level_num)

    # Put back what an older version would have stored: one short of the last.
    data = bytearray(path.read_bytes())
    section_size = INT_SIZE_IN_BYTES + bundle.num_levels * LEVEL_SCORE_SIZE_IN_BYTES
    unlocked_offset = len(data) - section_size
    data[unlocked_offset:unlocked_offset + INT_SIZE_IN_BYTES] = (last_level - 1).to_bytes(
        INT_SIZE_IN_BYTES, byteorder="big")
    path.write_bytes(data)

    reloaded = create_or_load_profile(bundle, path)
    assert reloaded.is_level_unlocked(last_level)
