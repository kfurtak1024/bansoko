"""Module exposing animation related classes."""
from typing import NamedTuple, Optional

from bansoko.graphics import Point, Direction, Layer
from bansoko.graphics.sprite import Sprite


class Animation(NamedTuple):
    """Animation exposes information needed for playing a sequence of frames stored in a sprite.

    Attributes:
        sprite - sprite containing animation frame
        frame_length - the length of the single frame (expressed in ms)
        looped - should animation be played from the beginning after reaching the last frame
    """
    sprite: Sprite
    frame_length: float
    looped: bool = False

    @property
    def animation_length(self) -> float:
        """Total animation length (expressed in ms)."""
        return self.num_frames * self.frame_length

    @property
    def num_frames(self) -> int:
        """Total number of frames in the animation."""
        return self.sprite.num_frames

    @property
    def last_frame(self) -> int:
        """Index of the last frame of the animation."""
        return self.num_frames - 1

    def frame_at_time(self, animation_time: float) -> int:
        """Return index of the animation frame corresponding to given animation time.

        :param animation_time: animation time to find frame at (expressed in ms)
        :return: the index of animation frame corresponding to given animation time
        """
        frame = round(animation_time / self.frame_length)
        return frame % self.num_frames if self.looped else min(self.last_frame, frame)


class AnimationPlayer:
    animation: Optional[Animation] = None
    current_frame: int = 0
    animation_time: float = 0.0

    def __init__(self, animation: Optional[Animation] = None) -> None:
        if animation:
            self.play(animation)

    def play(self, animation: Animation) -> None:
        self.animation = animation
        self.current_frame = 0
        self.animation_time = 0.0

    def update(self, dt_in_ms: float) -> None:
        """Update animation player with time that elapsed over a single game frame.

        It updates total animation time and calculates the current animation frame.

        :param dt_in_ms: delta time since last update (in ms)
        """
        if not self.animation:
            return

        self.animation_time += dt_in_ms
        self.current_frame = self.animation.frame_at_time(self.animation_time)

    def draw(self, position: Point, layer: Optional[Layer] = None,
             direction: Direction = Direction.UP) -> None:
        """Draw current animation frame at given position using specified layer and direction.

        Current frame is calculated based on elapsed animation time.

        :param position: position of animation frame to be drawn at
        :param layer: layer of animation frame to be drawn at
        :param direction: direction-specific variant of animation frame to be drawn
        """
        if not self.animation:
            return

        self.animation.sprite.draw(position, layer=layer, direction=direction,
                                   frame=self.current_frame)
