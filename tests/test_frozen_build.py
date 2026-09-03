"""Smoke test for the standalone PyInstaller builds.

A frozen build can compile perfectly and still fail on launch, because the
game resolves its resources relative to __file__ and PyInstaller changes
where that points. That failure is invisible to every other test here, and
it ships straight to players on itch.io, so the release workflow builds the
binary and then points this test at it.

Set BANSOKO_FROZEN_BINARY to the built executable to enable these.

The version check needs no graphics and so runs anywhere; the startup check
needs working OpenGL, because the game opens a real window.
"""
import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple

import pytest

# The game runs until the player quits, so it is expected to outlive this.
STARTUP_TIMEOUT_SECONDS = 30



def run_binary(binary: Path, work_dir: Path, env: dict,
               timeout: float) -> Tuple[Optional[int], str]:
    """Run the binary, capturing output through files rather than pipes.

    subprocess.run(capture_output=True, timeout=...) is not safe here. Its
    timeout kills the process it started, but PyInstaller's one-file
    bootloader on Windows launches a second process that inherits the pipe
    handles; the reader threads then never see EOF and communicate() blocks
    for ever, timeout or no timeout. That is exactly how a release run came
    to sit for hours on a binary that hung at startup.

    Writing to files means there are no reader threads to join, so the
    timeout is real on every platform.

    :return: (returncode, combined output). returncode is None if it was
             still running when the timeout expired, which is the healthy
             outcome for a game that has started successfully.
    """
    out_path = work_dir / "stdout.txt"
    err_path = work_dir / "stderr.txt"
    with open(out_path, "wb") as out, open(err_path, "wb") as err:
        process = subprocess.Popen(  # pylint: disable=consider-using-with
            [str(binary)], cwd=work_dir, env=env, stdout=out, stderr=err)
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            code = None

    output = out_path.read_text(encoding="utf-8", errors="replace")
    output += err_path.read_text(encoding="utf-8", errors="replace")
    return code, output


def test_frozen_binary_reports_its_version(frozen_binary: Path, tmp_path: Path) -> None:
    """--version must work without any graphics.

    argparse handles it and exits before pyxel.init(), so this runs even on a
    machine with no OpenGL driver. It proves the executable runs at all: the
    interpreter, the bundled modules and the entry point are intact.
    """
    out_path = tmp_path / "stdout.txt"
    err_path = tmp_path / "stderr.txt"
    with open(out_path, "wb") as out, open(err_path, "wb") as err:
        process = subprocess.Popen(  # pylint: disable=consider-using-with
            [str(frozen_binary), "--version"], cwd=tmp_path, stdout=out, stderr=err)
        try:
            code = process.wait(timeout=STARTUP_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            pytest.fail(
                f"--version did not finish within {STARTUP_TIMEOUT_SECONDS}s. The "
                "binary hangs at startup; it is not usable.")

    printed = out_path.read_text(encoding="utf-8", errors="replace")
    assert code == 0, (
        f"--version exited {code}\n{printed}"
        f"{err_path.read_text(encoding='utf-8', errors='replace')}")
    assert printed.strip(), "--version printed nothing"


def test_frozen_binary_starts_and_loads_resources(frozen_binary: Path,
                                                  graphics: None,
                                                  tmp_path: Path) -> None:
    """The binary must reach "Game started." with its bundled resources."""
    del graphics  # Depended on for its skip/fail behaviour only.
    home = tmp_path / "home"
    home.mkdir()
    env = {**os.environ, "HOME": str(home), "USERPROFILE": str(home)}

    code, output = run_binary(frozen_binary, tmp_path, env, STARTUP_TIMEOUT_SECONDS)
    if code is not None:
        pytest.fail(f"Binary exited early with code {code}.\n{output}")

    log = home / ".bansoko" / "bansoko.log"
    assert log.is_file(), (
        f"No log at {log}; the binary never got as far as configuring logging.")
    contents = log.read_text(encoding="utf-8", errors="replace")
    assert "Game started." in contents, (
        "Binary started but did not finish loading its bundled resources. This "
        "usually means the gamedata mapping in bansoko.spec no longer matches "
        f"where __file__ resolves inside the bundle.\n\nLog:\n{contents}")
