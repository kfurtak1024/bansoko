"""Tests that every screen in the game still renders.

The frozen-build smoke test only ever exercises the main menu, because that
is the screen the game happens to open on. Everything else --- the playfield,
the level browser, the pause and completion screens --- was never drawn by
any automated check.

These construct each screen and draw it for real, against an initialised
Pyxel. That covers the drawing API the game leans on (blt, bltm, text, rect,
rectb, line, cls) across the whole UI, which is exactly the surface a Pyxel
upgrade can break without changing a single type signature.
"""
from typing import Callable, List, Set, Tuple

import pytest
import pyxel

from bansoko.game.context import GameContext
from bansoko.game.profile import LevelScore
from bansoko.game.screens.error import ErrorScreen
from bansoko.graphics import SCREEN_HEIGHT, SCREEN_WIDTH
from bansoko.gui.navigator import ScreenController

FRAME_MS = 1000 / 30

# Sampling every pixel means 65k pget calls per screen; a grid is enough to
# tell "something was drawn" from "the screen stayed blank".
SAMPLE_STEP = 4

ScreenBuilder = Tuple[str, Callable[[GameContext], ScreenController]]

SCREENS: List[ScreenBuilder] = [
    ("main_menu", lambda ctx: ctx.get_main_menu()),
    ("choose_level", lambda ctx: ctx.get_choose_level_screen()),
    ("playfield", lambda ctx: ctx.get_playfield_screen(0)),
    ("playfield_without_how_to_play",
     lambda ctx: ctx.get_playfield_screen(0, skip_how_to_play=True)),
    ("game_paused", lambda ctx: ctx.get_game_paused_screen(0)),
    ("level_completed",
     lambda ctx: ctx.get_level_completed_screen(
         LevelScore(level_num=0, completed=True, pushes=7, steps=19, time_in_ms=12_345))),
    ("how_to_play", lambda ctx: ctx.get_how_to_play_screen()),
    ("victory", lambda ctx: ctx.get_victory_screen()),
    ("exit", lambda ctx: ctx.get_exit_screen(lambda: None)),
]

SCREEN_IDS = [name for name, _ in SCREENS]


def sampled_colors() -> Set[int]:
    """Colours currently on screen, sampled on a grid."""
    return {
        pyxel.screen.pget(x, y)
        for y in range(0, SCREEN_HEIGHT, SAMPLE_STEP)
        for x in range(0, SCREEN_WIDTH, SAMPLE_STEP)
    }


def render(controller: ScreenController, as_secondary: bool = False) -> Set[int]:
    """Draw a screen onto a cleared framebuffer and report what landed."""
    pyxel.cls(0)
    controller.draw(draw_as_secondary=as_secondary)
    return sampled_colors()


@pytest.mark.parametrize("builder", [b for _, b in SCREENS], ids=SCREEN_IDS)
def test_screen_draws_something(
        game_context: GameContext,
        builder: Callable[[GameContext], ScreenController]) -> None:
    """Each screen must construct, activate and put pixels on the display.

    Asserting more than one colour is what distinguishes a screen that
    rendered from one that raised nothing and drew nothing.
    """
    controller = builder(game_context)
    controller.activate()
    colors = render(controller)
    assert len(colors) > 1, "screen drew nothing onto a cleared framebuffer"


@pytest.mark.parametrize("builder", [b for _, b in SCREENS], ids=SCREEN_IDS)
def test_screen_draws_as_secondary(
        game_context: GameContext,
        builder: Callable[[GameContext], ScreenController]) -> None:
    """Screens are also drawn underneath others, which is a separate path.

    Semi-transparent screens take a different branch here, so a break in it
    would otherwise only show up behind a pause or completion overlay.
    """
    controller = builder(game_context)
    controller.activate()
    render(controller, as_secondary=True)


@pytest.mark.parametrize("builder", [b for _, b in SCREENS], ids=SCREEN_IDS)
def test_screen_updates_without_input(
        game_context: GameContext,
        builder: Callable[[GameContext], ScreenController]) -> None:
    """A frame of update with no keys pressed must not raise.

    This is the path that reads pyxel.btn/btnp and the KEY_* and GAMEPAD1_*
    constants, none of which any other test touches.
    """
    controller = builder(game_context)
    controller.activate()
    controller.update(FRAME_MS)


def test_error_screen_draws(pyxel_runtime: None) -> None:
    """The error screen is built outside the factory, when loading fails.

    It is the one screen a player only ever sees when something has already
    gone wrong, so it is the worst one to have quietly broken.
    """
    del pyxel_runtime  # Ordering dependency: resources must be loaded first.
    controller = ErrorScreen("Something went wrong")
    controller.activate()
    pyxel.cls(0)
    controller.draw()
    assert len(sampled_colors()) > 1, "error screen drew nothing"
