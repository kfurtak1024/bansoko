"""Tests for the geometry and text helpers the screens are laid out with."""
import pyxel

from bansoko.graphics import Point, Size
from bansoko.graphics.text import draw_text, escape_text, text_size


def test_enlarge_grows_both_dimensions_by_one_amount() -> None:
    """With a single argument the size grows evenly."""
    assert Size(10, 20).enlarge(2) == Size(12, 22)


def test_enlarge_by_zero_height_leaves_the_height_alone() -> None:
    """Zero is an amount, not a request to reuse the width's."""
    assert Size(10, 20).enlarge(8, 0) == Size(18, 20)


def test_sizes_are_ordered_by_width_then_height() -> None:
    """Sizes compare with each other, which is what sorting them needs."""
    assert Size(1, 9) < Size(2, 0)
    assert Size(2, 1) < Size(2, 3)
    assert Size(3, 3) >= Size(3, 3)
    assert sorted([Size(2, 2), Size(1, 5)]) == [Size(1, 5), Size(2, 2)]


def test_a_colour_tag_takes_no_room() -> None:
    """A tag and its colour digit are instructions, not characters."""
    assert text_size("#8RED") == text_size("RED")


def test_a_doubled_tag_is_one_character() -> None:
    """Writing the tag twice draws it once."""
    assert text_size("##").width == pyxel.FONT_WIDTH


def test_a_tag_without_a_colour_is_measured_as_written() -> None:
    """A tag followed by something that is not a colour is ordinary text."""
    assert text_size("#x").width == 2 * pyxel.FONT_WIDTH


def test_escaped_text_is_as_wide_as_it_reads() -> None:
    """Escaping makes foreign text draw exactly as it is, colour tags included."""
    path = "/home/#abc/save #1"
    assert text_size(escape_text(path)).width == len(path) * pyxel.FONT_WIDTH


def test_a_tag_without_a_colour_can_be_drawn(pyxel_runtime: None) -> None:
    """Drawing such text used to raise; it must draw."""
    del pyxel_runtime  # Depended on for the window only.
    draw_text(Point(0, 0), "50% #off, see #")
