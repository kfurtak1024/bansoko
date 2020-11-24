"""Module exposing Sprite type."""
from dataclasses import dataclass
from typing import Tuple, Optional

import pyxel

from bansoko.graphics import Rect, Point, Direction, Layer


@dataclass(frozen=True)
class Sprite:
    """Sprite is a part of an Image that can be drawn on screen at given position.

    The exact fragment of the image is defined by image_bank and uv_rect (which is a rectangle in
    image space)
    Additionally, sprite can be:
    - multilayer - it contains variants for all layers,
    - directional - it contains variants for all 4 directions,
    - transparent - it is drawn with transparency color (-1 means opaque)
    - multiframe - it contains multiple frames (for example for animation purposes)

    Please note that those features can be combined, so we can have sprite which is multilayer,
    directional and multiframe at the same time.
    """
    image_bank: int
    uv_rect: Rect
    directional: bool = False
    transparency_color: int = -1
    num_layers: int = 1
    num_frames: int = 1

    def draw(self, position: Point, layer: Optional[Layer] = None,
             direction: Direction = Direction.UP, frame: int = 0) -> None:
        """Draw the sprite at given position using specified layer, direction and frame.

        If sprite is single-layered then it will be drawn _only on main_ layer.

        :param position: position of sprite to be drawn at
        :param layer: layer of sprite to be drawn at
        :param direction: direction-specific variant of sprite to be drawn
        :param frame: frame of sprite to be drawn
        """
        if layer and layer.layer_index >= self.num_layers:
            return

        clamped_frame = min(frame, self.num_frames - 1)
        frame_offset_v = clamped_frame * self.uv_rect.h // self.num_frames
        top_layer_offset = self.num_layers - 1

        u = self.uv_rect.x + top_layer_offset
        v = self.uv_rect.y + frame_offset_v + top_layer_offset

        if self.directional:
            u += self.uv_rect.w // Direction.num_directions() * direction.direction_index

        if layer:
            u -= layer.layer_index
            v -= layer.layer_index

        offset = layer.offset if layer else Point(0, 0)

        pyxel.blt(position.x + offset.x, position.y + offset.y, self.image_bank,
                  u, v, self.width, self.height, self.transparency_color)

    @property
    def width(self) -> int:
        """The width of sprite in pixels."""
        width = self.uv_rect.w

        if self.directional:
            width //= Direction.num_directions()

        width -= self.num_layers - 1

        return width

    @property
    def height(self) -> int:
        """The height of sprite in pixels."""
        return self.uv_rect.h // self.num_frames - (self.num_layers - 1)


@dataclass(frozen=True)
class SpritePack:
    """Sprite Pack is a collection of sprites, grouped together for organizational purposes."""
    sprites: Tuple[Sprite, ...]
