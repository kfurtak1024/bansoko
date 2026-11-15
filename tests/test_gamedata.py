"""Tests that the committed game data is valid and matches its source assets.

The resource builder is the only way to produce bansoko/gamedata, and its
output is checked into the repository. These tests guard the two things
that can silently go wrong: the committed data drifting away from the
assets it was built from, and a Pyxel upgrade changing the generated
format underneath us.
"""
import json
from pathlib import Path

import pytest
from jsonschema import validate

from bansoko.game import GameError
from bansoko.game.bundle import Bundle, load_bundle
from bansoko.game.metadata_schema import METADATA_JSON_SCHEMA


def test_committed_gamedata_is_present(gamedata_dir: Path) -> None:
    """Both generated files must be checked in for the game to run."""
    assert (gamedata_dir / "main.meta").is_file()
    assert (gamedata_dir / "main.pyxres").is_file()


def test_committed_metadata_matches_schema(gamedata_dir: Path) -> None:
    """The metadata must satisfy the schema the game validates it against."""
    metadata = json.loads((gamedata_dir / "main.meta").read_text(encoding="utf-8"))
    validate(metadata, METADATA_JSON_SCHEMA)


def test_committed_metadata_loads_as_a_bundle(bundle: Bundle) -> None:
    """The metadata must produce a usable bundle, not just valid JSON."""
    assert bundle.num_levels > 0
    assert bundle.last_level == bundle.num_levels - 1
    assert len(bundle.sha1) == 40
    assert bundle.sprites and bundle.sprite_packs and bundle.screens


def test_metadata_uses_lf_newlines(gamedata_dir: Path) -> None:
    """Output must not depend on the platform it was built on.

    json.dump writes platform-native newlines unless told otherwise, which
    makes the file differ between Windows and Linux builds even when the
    content is identical.
    """
    assert b"\r\n" not in (gamedata_dir / "main.meta").read_bytes()


def test_committed_gamedata_matches_source_assets(built_resources: Path,
                                                  gamedata_dir: Path) -> None:
    """A fresh build of resources/main.ressrc must reproduce what is committed.

    Both outputs are byte-reproducible, so this is an exact comparison. If it
    fails, either the assets changed without the builder being re-run, or the
    builder's output format changed.
    """
    for name in ("main.meta", "main.pyxres"):
        assert (built_resources / name).read_bytes() == (gamedata_dir / name).read_bytes(), (
            f"{name} differs from a fresh build of resources/main.ressrc. Re-run: "
            f"python -m resbuilder resources/main.ressrc --outdir bansoko/gamedata --force")


def test_bundle_sha1_is_stable(built_resources: Path, bundle: Bundle) -> None:
    """The bundle SHA1 keys player profiles, so changing it invalidates saves."""
    rebuilt = json.loads((built_resources / "main.meta").read_text(encoding="utf-8"))
    assert rebuilt["levels"]["sha1"].encode() == bytes(bundle.sha1)


def test_a_missing_metadata_file_is_a_game_error(tmp_path: Path) -> None:
    """Whatever stops the metadata loading must reach the in-game error screen."""
    with pytest.raises(GameError):
        load_bundle(str(tmp_path / "missing.meta"))


def test_a_dangling_reference_is_a_game_error(gamedata_dir: Path, tmp_path: Path) -> None:
    """Metadata can match the schema and still name a sprite that is not there.

    A mod is the likely way to get one, and its author needs the name of what
    is missing, not a traceback.
    """
    metadata = json.loads((gamedata_dir / "main.meta").read_text(encoding="utf-8"))
    pack_name = next(iter(metadata["sprite_packs"]))
    metadata["sprite_packs"][pack_name][0] = "no_such_sprite"
    broken = tmp_path / "broken.meta"
    broken.write_text(json.dumps(metadata), encoding="utf-8")

    with pytest.raises(GameError) as raised:
        load_bundle(str(broken))
    assert "no_such_sprite" in raised.value.message


def test_a_game_error_says_what_went_wrong() -> None:
    """The message has to survive into the log, which prints the exception itself."""
    assert str(GameError("Something specific")) == "Something specific"
