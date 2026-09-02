"""Tests for the Sokoban rules: can the game still actually be played?

These drive real levels from the committed game data through Level's public
API, the same way the playfield screen does. They are the answer to "does the
game still work" that no amount of import checking can give.

Level layouts come from the tilemaps in main.pyxres, so Pyxel has to be
initialised; the rules themselves touch no Pyxel API at all.
"""
from typing import List

from bansoko.game.bundle import Bundle
from bansoko.game.level import InputAction, Level

MOVE_RIGHT = InputAction.MOVE_RIGHT
MOVE_LEFT = InputAction.MOVE_LEFT
MOVE_UP = InputAction.MOVE_UP
MOVE_DOWN = InputAction.MOVE_DOWN

FRAME_MS = 1000 / 30

# Level 0 is the tutorial: one crate, one cargo bay, in a small U-shaped room.
# The crate is pushed right until it hits a wall, then up, then right into the
# bay. Level data is pinned by the game data tests, so if a change to the
# layout breaks this, that is a real signal and both should be updated.
LEVEL_0_SOLUTION = [
    MOVE_RIGHT, MOVE_RIGHT, MOVE_RIGHT,
    MOVE_LEFT, MOVE_DOWN, MOVE_DOWN, MOVE_RIGHT, MOVE_RIGHT, MOVE_UP,
    MOVE_UP, MOVE_UP,
    MOVE_DOWN, MOVE_LEFT, MOVE_LEFT, MOVE_UP, MOVE_UP, MOVE_RIGHT,
    MOVE_RIGHT, MOVE_RIGHT,
]


def settle(level: Level) -> None:
    """Advance the level until the queued action has finished.

    Moves are animated over several frames, so the effect of an input is not
    visible until the action completes.
    """
    for _ in range(1000):
        if not level.running_action:
            return
        level.update(FRAME_MS)
    raise AssertionError("action never finished")


def play(level: Level, moves: List[InputAction]) -> None:
    """Apply a sequence of inputs, letting each one complete."""
    for move in moves:
        level.process_input(move)
        settle(level)


def test_level_starts_incomplete_with_a_crate(level: Level) -> None:
    """A level begins unsolved, with at least one crate out of place."""
    assert level.crates
    assert not level.is_completed
    assert not all(crate.in_place for crate in level.crates)
    assert level.statistics.steps == 0
    assert level.statistics.pushes == 0


def test_robot_moves_into_free_space(level: Level) -> None:
    """Moving into open floor changes position and counts a step."""
    start = level.robot.tile_position
    play(level, [MOVE_RIGHT])
    assert level.robot.tile_position != start
    assert level.statistics.steps == 1


def test_wall_blocks_movement(level: Level) -> None:
    """Walking into a wall turns the robot but does not move it."""
    start = level.robot.tile_position
    # The tutorial room is one tile high where the robot starts, so up and
    # down are both walls.
    play(level, [MOVE_UP, MOVE_DOWN])
    assert level.robot.tile_position == start


def test_pushing_a_crate_moves_robot_and_crate(level: Level) -> None:
    """Pushing moves both the robot and the crate, and counts a push."""
    crate = level.crates[0]
    robot_before = level.robot.tile_position
    crate_before = crate.tile_position

    play(level, [MOVE_RIGHT])

    assert level.robot.tile_position == crate_before, "robot should take the crate's tile"
    assert crate.tile_position != crate_before, "crate should have been pushed"
    assert level.robot.tile_position != robot_before
    assert level.statistics.pushes == 1


def test_undo_restores_the_previous_position(level: Level) -> None:
    """Undo steps the robot back and empties the history."""
    start = level.robot.tile_position
    play(level, [MOVE_RIGHT])
    assert level.robot.tile_position != start

    play(level, [InputAction.UNDO])
    assert level.robot.tile_position == start
    assert not level.history


def test_undo_puts_a_pushed_crate_back(level: Level) -> None:
    """Undoing a push returns the crate as well as the robot."""
    crate = level.crates[0]
    crate_start = crate.tile_position
    play(level, [MOVE_RIGHT])
    assert crate.tile_position != crate_start

    play(level, [InputAction.UNDO])
    assert crate.tile_position == crate_start


def test_undo_on_a_fresh_level_does_nothing(level: Level) -> None:
    """There is nothing to undo at the start, and that must not raise."""
    start = level.robot.tile_position
    play(level, [InputAction.UNDO])
    assert level.robot.tile_position == start


def test_level_can_be_completed(level: Level) -> None:
    """The tutorial level can be solved, and reports itself completed.

    This is the end-to-end check that the rules still work: movement,
    collision, crate pushing and the victory condition all have to be correct
    for the crate to reach the cargo bay.
    """
    assert not level.is_completed
    play(level, LEVEL_0_SOLUTION)

    assert level.is_completed, (
        f"level not solved; robot at {level.robot.tile_position}, "
        f"crate at {level.crates[0].tile_position}")
    assert all(crate.in_place for crate in level.crates)


def test_completed_level_reports_its_score(level: Level) -> None:
    """A solved level produces a score that the profile can store."""
    play(level, LEVEL_0_SOLUTION)
    score = level.level_score

    assert score.completed
    assert score.level_num == level.level_num
    assert score.steps == len(LEVEL_0_SOLUTION)
    assert 0 < score.pushes <= score.steps
    assert score.time_in_ms > 0


def test_every_level_template_builds(pyxel_runtime: None, bundle: Bundle) -> None:
    """All levels in the bundle must construct, not just the first.

    A level with no start tile or a malformed tilemap raises on construction,
    so this walks the whole campaign.
    """
    del pyxel_runtime  # Ordering dependency: resources must be loaded first.
    for level_num in range(bundle.num_levels):
        built = Level(bundle.get_level_template(level_num))
        assert built.level_num == level_num
        assert built.crates, f"level {level_num} has no crates"
        assert not built.is_completed, f"level {level_num} starts already solved"
