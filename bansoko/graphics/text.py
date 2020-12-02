"""Module exposing text drawing related routines."""
from dataclasses import dataclass
from typing import Optional

import pyxel

from bansoko.graphics import Size, Point


@dataclass(frozen=True)
class TextStyle:
    """TextStyle defines basic properties used when text is drawn."""
    color: int = 7
    shadow_color: Optional[int] = None
    vertical_space: int = 0


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
        if char == '#':
            color_tag = not color_tag
            if color_tag:
                continue

        if color_tag:
            color_tag = False
        else:
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
        if char == '#':
            color_tag = not color_tag
            if color_tag:
                continue

        if color_tag:
            current_color = int(char, 16)
            color_tag = False
        else:
            if style.shadow_color is not None:
                pyxel.text(x + 1, y + 1, char, style.shadow_color)
            pyxel.text(x, y, char, current_color)
            x += pyxel.FONT_WIDTH
