from typing import NamedTuple

import pyxel

from bansoko.graphics import Size


class TextStyle(NamedTuple):
    color: int = 7
    shadow: bool = False
    vertical_space: int = 0


def text_size(text: str, style: TextStyle) -> Size:
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


def draw_text(x0: int, y0: int, text: str, style: TextStyle) -> None:
    x = x0
    y = y0
    current_color = style.color
    color_tag = False
    for char in text:
        if char == '\n':
            x = x0
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
            if style.shadow:
                pyxel.text(x + 1, y + 1, char, 0)
            pyxel.text(x, y, char, current_color)
            x += pyxel.FONT_WIDTH
