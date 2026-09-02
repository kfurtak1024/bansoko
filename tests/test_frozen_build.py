"""Smoke test for the standalone PyInstaller builds.

A frozen build can compile perfectly and still fail on launch, because the
game resolves its resources relative to __file__ and PyInstaller changes
where that points. That failure is invisible to every other test here, and
it ships straight to players on itch.io, so the release workflow builds the
binary and then points this test at it.

Set BANSOKO_FROZEN_BINARY to the built executable to enable it.
"""
import os
import subprocess
from pathlib import Path

import pytest

# The game runs until the player quits, so it is expected to outlive this.
STARTUP_TIMEOUT_SECONDS = 30


def test_frozen_binary_starts_and_loads_resources(frozen_binary: Path,
                                                  tmp_path: Path) -> None:
    """The binary must reach "Game started." with its bundled resources."""
    home = tmp_path / "home"
    home.mkdir()
    env = {**os.environ, "HOME": str(home), "USERPROFILE": str(home)}

    try:
        completed = subprocess.run(
            [str(frozen_binary)], cwd=tmp_path, env=env, capture_output=True,
            text=True, timeout=STARTUP_TIMEOUT_SECONDS, check=False)
    except subprocess.TimeoutExpired:
        pass  # Still running after startup is exactly what we want.
    else:
        pytest.fail(
            f"Binary exited early with code {completed.returncode}.\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}")

    log = home / ".bansoko" / "bansoko.log"
    assert log.is_file(), (
        f"No log at {log}; the binary never got as far as configuring logging.")
    contents = log.read_text(encoding="utf-8", errors="replace")
    assert "Game started." in contents, (
        "Binary started but did not finish loading its bundled resources. This "
        "usually means the gamedata mapping in bansoko.spec no longer matches "
        f"where __file__ resolves inside the bundle.\n\nLog:\n{contents}")
