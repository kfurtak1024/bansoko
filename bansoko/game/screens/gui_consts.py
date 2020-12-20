"""Module exposing all Gui constants."""
from dataclasses import dataclass
from enum import unique, Enum
from typing import Tuple, Any

from bansoko.graphics import Point
from bansoko.graphics.sprite import Sprite


class GuiConstant(Enum):
    """Base enum class for all Gui constants."""

    def __new__(cls) -> Any:
        value = len(cls.__members__)
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    @property
    def resource_name(self) -> str:
        """The name of the resource from metadata file."""
        return str(self.name).casefold()

    @property
    def resource_index(self) -> int:
        """The index of the resource in the array of constants."""
        return int(self.value)


@unique
class GuiPosition(GuiConstant):
    """All Gui positions that are required by the game's Gui."""
    LEVEL_ITEM_SIZE = ()
    LEVEL_ITEM_SPACE = ()
    LEVEL_ITEM_TITLE_POS = ()
    LEVEL_LOCKED_ICON_POS = ()
    LEVEL_COMPLETED_ICON_POS = ()
    LEVEL_THUMBNAIL_POS = ()
    LEVEL_SCORE_POS = ()
    COCKPIT_LEVEL_NUM_POS = ()
    COCKPIT_LEVEL_TIME_POS = ()
    COCKPIT_LEVEL_STEPS_POS = ()
    COCKPIT_LEVEL_PUSHES_POS = ()
    COCKPIT_JOYSTICK_POS = ()
    COCKPIT_REWIND_BUTTON_POS = ()
    COCKPIT_RECEIPT_POS = ()
    COCKPIT_REWIND_ICON_POS = ()
    LEFT_HAND_NEUTRAL_POS = ()
    LEFT_HAND_LEFT_POS = ()
    LEFT_HAND_RIGHT_POS = ()
    LEFT_HAND_UP_POS = ()
    LEFT_HAND_DOWN_POS = ()
    LEFT_HAND_PRESSING_BUTTON_POS = ()


@unique
class GuiColor(GuiConstant):
    """All Gui colors that are required by the game's Gui."""
    LEVEL_SELECTED_COLOR = ()
    LEVEL_LOCKED_COLOR = ()
    LEVEL_UNLOCKED_COLOR = ()
    LEVEL_COMPLETED_COLOR = ()


@unique
class GuiSprite(GuiConstant):
    """All Gui sprites that are required by the game's Gui."""
    CHECKED_ICON = ()
    LOCKED_ICON = ()
    LEVEL_DIGITS = ()
    STEPS_DIGITS = ()
    PUSHES_DIGITS = ()
    TIME_DIGITS = ()
    REWIND_ICON = ()
    JOYSTICK_NEUTRAL = ()
    JOYSTICK_MOVE = ()
    REWIND_BUTTON = ()
    LEFT_HAND = ()
    LEFT_HAND_PRESSING_BUTTON = ()


@dataclass(frozen=True)
class GuiConsts:
    """Collection of Gui constants like positions, colors and sprites."""
    gui_positions: Tuple[Point, ...]
    gui_colors: Tuple[int, ...]
    gui_sprites: Tuple[Sprite, ...]

    def get_position(self, gui_position_id: GuiPosition) -> Point:
        """Get Gui element position for given id."""
        return self.gui_positions[gui_position_id.resource_index]

    def get_color(self, gui_color_id: GuiColor) -> int:
        """Get Gui element color for given id."""
        return self.gui_colors[gui_color_id.resource_index]

    def get_sprite(self, gui_sprite_id: GuiSprite) -> Sprite:
        """Get Gui element sprite for given id."""
        return self.gui_sprites[gui_sprite_id.resource_index]
