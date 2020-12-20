"""Module exposing animation related classes."""
from dataclasses import dataclass
from typing import Optional

from bansoko.graphics import Point, Direction, Layer
from bansoko.graphics.sprite import Sprite


@dataclass(frozen=True)
class Animation:
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

    def frame_at_time(self, animation_time: float, playing_backwards: bool = False) -> int:
        """Return index of the animation frame corresponding to given animation time.

        :param animation_time: animation time to find frame at (expressed in ms)
        :param playing_backwards: is animation being played backwards
        :return: the index of animation frame corresponding to given animation time
        """
        frame_num = round(animation_time / self.frame_length)
        frame = frame_num % self.num_frames if self.looped else min(self.last_frame, frame_num)
        return frame if not playing_backwards else self.last_frame - frame

    def stopped_at_time(self, animation_time: float) -> bool:
        """Check if the animation will be stopped at given animation time.

        :param animation_time: animation time to be checked
        :return: True if animation will be stopped (not played) at given time; False otherwise
        """
        return not self.looped and animation_time > self.animation_length


@dataclass
class AnimationPlayer:
    """Player for animations.

    Call to AnimationPlayer's update() is required in each frame.

    Attributes:
        animation - animation that is played by the animation player
        current_frame - the current frame of the animation (according to animation_time)
        animation_time - elapsed animation time (updated in each call to update())
    """
    animation: Optional[Animation] = None
    current_frame: int = 0
    animation_time: float = 0.0
    backwards: bool = False

    def play(self, animation: Animation, backwards: bool = False) -> None:
        """Set up the animation player to play given animation.

        :param animation: animation to be played
        :param backwards: shall animation be played backwards
        """
        self.animation = animation
        self.current_frame = 0
        self.animation_time = 0.0
        self.backwards = backwards

    def update(self, dt_in_ms: float) -> None:
        """Update animation player with time that elapsed over a single game frame.

        It updates total animation time and calculates the current animation frame.

        :param dt_in_ms: delta time since last update (in ms)
        """
        if not self.animation:
            return

        self.animation_time += dt_in_ms
        self.current_frame = self.animation.frame_at_time(self.animation_time, self.backwards)

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

    @property
    def stopped(self) -> bool:
        """Is animation player stopped.

        Animation player is stopped when it has no animation *OR* animation is not looped and was
        played already.
        """
        return not self.animation or self.animation.stopped_at_time(self.animation_time)
