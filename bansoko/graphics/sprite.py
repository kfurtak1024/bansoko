"""Module exposing Sprite type."""
from typing import NamedTuple, Tuple

import pyxel

from bansoko.graphics import Rect, Point, Direction, Layer


class Sprite(NamedTuple):
    """Sprite is a part of an Image that can be drawn on screen at given position.

    The exact fragment of the image is defined by image_bank and uv_rect (which is a rectangle in
    image space)
    Additionally, sprite can be:
    - multilayer - it contains variants for all 3 layers,
    - directional - it contains variants for all 4 directions,
    - multiframe - it contains multiple frames (for example for animation purposes)

    Please note that those features can be combined, so we can have sprite which is multilayer,
    directional and multiframe at the same time.
    """
    image_bank: int
    uv_rect: Rect
    multilayer: bool = False
    directional: bool = False
    num_frames: int = 1

    def draw(self, position: Point, layer: Layer = Layer.LAYER_0,
             direction: Direction = Direction.UP, frame: int = 0) -> None:
        """Draw the sprite at given position using specified layer, direction and frame.

        If sprite is single-layered then it will be drawn _only on main_ layer.

        :param position: position of sprite to be drawn at
        :param layer: layer of sprite to be drawn at
        :param direction: direction-specific variant of sprite to be drawn
        :param frame: frame of sprite to be drawn
        """
        if not self.multilayer and not layer.is_main:
            return

        clamped_frame = min(frame, self.num_frames - 1)

        x = self.uv_rect.x + clamped_frame * self.uv_rect.w // self.num_frames
        y = self.uv_rect.y

        if self.directional:
            x += self.uv_rect.w // Direction.num_directions() * direction.direction_index

        if self.multilayer:
            top_layer = Layer.LAYER_2.layer_index
            x += top_layer + layer.offset.x
            y += top_layer + layer.offset.y

        pyxel.blt(position.x + layer.offset.x, position.y + layer.offset.y, self.image_bank, x,
                  y, self.width, self.height, 0)

    @property
    def width(self) -> int:
        """The width of sprite in pixels."""
        width = self.uv_rect.w // self.num_frames

        if self.directional:
            width //= Direction.num_directions()

        if self.multilayer:
            top_layer = Layer.LAYER_2.layer_index
            width -= top_layer

        return width

    @property
    def height(self) -> int:
        """The height of sprite in pixels."""
        height = self.uv_rect.h

        if self.multilayer:
            top_layer = Layer.LAYER_2.layer_index
            height -= top_layer

        return height


class SkinPack(NamedTuple):
    """SkinPack is a collection of sprites, grouped together for organizational purposes."""
    skin_sprites: Tuple[Sprite, ...]
