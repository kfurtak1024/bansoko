"""Tests for the resource builder's own rules: what it refuses, and how it fails.

The game data tests check what a good build produces. These check the other
half: that a build which cannot succeed says so and leaves the last good
output alone.
"""
import sys
from pathlib import Path
from typing import Any, List

import pytest
import pyxel

import resbuilder.__main__ as builder
from resbuilder import ResourceError
from resbuilder.resources.levels import _preprocess_level
from resbuilder.resources.tiles import Tile

ENCLOSED_LEVEL = [
    "XXXXXX",
    "X@ #+X",
    "XXXXXX",
]

# The same room with a gap in its right-hand wall.
OPEN_LEVEL = [
    "XXXXXX",
    "X@ #+ ",
    "XXXXXX",
]


def test_an_enclosed_level_gets_its_floor() -> None:
    """Floor is filled in from the start position, up to the walls."""
    level = _preprocess_level(0, ENCLOSED_LEVEL)
    assert level.tilemap_data.count(Tile.FLOOR) == 1
    assert level.tilemap_data.count(Tile.WALL) == 14


def test_a_level_with_a_gap_in_its_walls_is_refused() -> None:
    """A level the robot could walk out of must not be built."""
    with pytest.raises(ResourceError, match="Level 7 is not enclosed by walls"):
        _preprocess_level(7, OPEN_LEVEL)


def test_a_failed_build_exits_non_zero_and_writes_nothing(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A build that fails must not pass for one that worked, or damage the last one."""
    source = tmp_path / "main.ressrc"
    source.write_text("{}", encoding="utf-8")
    metadata = tmp_path / "main.meta"
    metadata.write_text("the last good build", encoding="utf-8")
    resource = tmp_path / "main.pyxres"
    resource.write_text("the last good build", encoding="utf-8")
    saved: List[str] = []

    def fail(*_args: Any) -> None:
        raise ResourceError("Level 3 is not enclosed by walls")

    monkeypatch.setattr(sys, "argv", ["resbuilder", str(source), "--outdir", str(tmp_path),
                                      "--force"])
    monkeypatch.setattr(builder, "validate", lambda *_args: None)
    monkeypatch.setattr(pyxel, "init", lambda **_kwargs: None)
    monkeypatch.setattr(pyxel, "save", saved.append)
    monkeypatch.setattr(builder, "create_metadata", fail)

    with pytest.raises(SystemExit) as exited:
        builder.main()

    assert exited.value.code == 1
    assert not saved
    assert metadata.read_text(encoding="utf-8") == "the last good build"
    assert resource.read_text(encoding="utf-8") == "the last good build"
