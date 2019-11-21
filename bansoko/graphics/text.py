from typing import NamedTuple

import pyxel

from graphics import Size


class TextAttributes(NamedTuple):
    color: int = 7
    shadow: bool = False
    vertical_space: int = 0


def text_size(text: str, attrib: TextAttributes) -> Size:
    text_width = 0
    text_height = 0
    line_width = 0
    color_tag = False
    for ch in text:
        if ch == '\n':
            text_width = max(text_width, line_width)
            text_height += pyxel.FONT_HEIGHT + attrib.vertical_space
            line_width = 0
            color_tag = False
            continue
        elif ch == '#':
            color_tag = not color_tag
            if color_tag:
                continue

        if color_tag:
            color_tag = False
        else:
            line_width += pyxel.FONT_WIDTH
    text_height -= attrib.vertical_space
    text_width = max(text_width, line_width)
    return Size(text_width, text_height)


def draw_text(x0: int, y0: int, text: str, attrib: TextAttributes) -> None:
    x = x0
    y = y0
    current_color = attrib.color
    color_tag = False
    for ch in text:
        if ch == '\n':
            x = x0
            y += pyxel.FONT_HEIGHT + attrib.vertical_space
            color_tag = False
            continue
        elif ch == '#':
            color_tag = not color_tag
            if color_tag:
                continue

        if color_tag:
            current_color = int(ch, 16)
            color_tag = False
        else:
            if attrib.shadow:
                pyxel.text(x + 1, y + 1, ch, 0)
            pyxel.text(x, y, ch, current_color)
            x += pyxel.FONT_WIDTH
