"""Module exposing text drawing related routines."""
from dataclasses import dataclass

import pyxel

from bansoko.graphics import Size, Point

COLOR_TAG = "#"
COLOR_DIGITS = "0123456789abcdefABCDEF"


@dataclass(frozen=True)
class TextStyle:
    """TextStyle defines basic properties used when text is drawn."""
    color: int = 7
    shadow_color: int | None = None
    vertical_space: int = 0


def escape_text(text: str) -> str:
    """Make text that this module did not write safe to draw.

    A path or an operating system message can contain the colour tag, and
    would otherwise change colour part way through or lose characters.

    :param text: text to be drawn exactly as it is
    :return: the same text, with every colour tag doubled so it is drawn as itself
    """
    return text.replace(COLOR_TAG, COLOR_TAG * 2)


def text_size(text: str, style: TextStyle = TextStyle()) -> Size:
    """Calculate the size of given text.

    Size represents the amount of screen space occupied by text during drawing.

    :param text: string to calculate size for
    :param style: text style calculation should be performed for
    :return: size of the string that will be used during text drawing
    """
    text_width = 0
    text_height = pyxel.FONT_HEIGHT
    line_width = 0
    color_tag = False
    for char in text:
        if char == '\n':
            text_width = max(text_width, line_width)
            text_height += pyxel.FONT_HEIGHT + style.vertical_space
            line_width = 0
            color_tag = False
            continue
        if char == COLOR_TAG:
            color_tag = not color_tag
            if color_tag:
                continue

        if color_tag:
            color_tag = False
            if char in COLOR_DIGITS:
                continue
            # Not a colour after all: the tag is drawn as it was written.
            line_width += pyxel.FONT_WIDTH
        line_width += pyxel.FONT_WIDTH
    text_height -= style.vertical_space
    text_width = max(text_width, line_width)
    return Size(text_width, text_height)


def draw_text(position: Point, text: str, style: TextStyle = TextStyle()) -> None:
    """Draws given text at specified position with defined text style.

    :param position: position of text to be drawn at
    :param text: text to be drawn
    :param style: style of text to be drawn with
    """
    x = position.x
    y = position.y
    current_color = style.color
    color_tag = False
    for char in text:
        if char == '\n':
            x = position.x
            y += pyxel.FONT_HEIGHT + style.vertical_space
            color_tag = False
            continue
        if char == COLOR_TAG:
            color_tag = not color_tag
            if color_tag:
                continue

        if color_tag:
            color_tag = False
            if char in COLOR_DIGITS:
                current_color = int(char, 16)
                continue
            # Not a colour after all: the tag is drawn as it was written.
            char = COLOR_TAG + char

        if style.shadow_color is not None:
            pyxel.text(x + 1, y + 1, char, style.shadow_color)
        pyxel.text(x, y, char, current_color)
        x += pyxel.FONT_WIDTH * len(char)
