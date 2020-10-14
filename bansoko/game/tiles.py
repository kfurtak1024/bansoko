"""Module exposing tile-related types."""
from dataclasses import dataclass
from enum import Enum, unique, auto


@unique
class TileType(Enum):
    """Enum representing type of a tile in terms of game logic."""
    VOID = auto()
    WALL = auto()
    START = auto()
    FLOOR = auto()
    INITIAL_CRATE_POSITION = auto()
    CRATE_INITIALLY_PLACED = auto()
    CARGO_BAY = auto()

    @property
    def is_start(self) -> bool:
        """Is tile a starting position for the player."""
        return self == TileType.START

    @property
    def is_crate_initially_placed(self) -> bool:
        """Is tile a cargo bay with already placed crate.

        Some crates are already placed in cargo bays at level start.
        """
        return self == TileType.CRATE_INITIALLY_PLACED

    @property
    def is_cargo_bay(self) -> bool:
        """Is tile a cargo bay.

        Cargo bays are the destinations to which crates should be moved to.
        """
        return self == TileType.CARGO_BAY

    @property
    def is_crate_spawn_point(self) -> bool:
        """Is tile a crate spawn point.

        Crate spawn point is a tile at which crate is placed during level initialization.
        """
        return self in (TileType.INITIAL_CRATE_POSITION, TileType.CRATE_INITIALLY_PLACED)

    @property
    def is_walkable(self) -> bool:
        """Is tile a walkable tile.

        A walkable tile means that:
        - player can move to it
        - crates can be pushed to it
        """
        return self in (TileType.START, TileType.FLOOR, TileType.INITIAL_CRATE_POSITION,
                        TileType.CRATE_INITIALLY_PLACED, TileType.CARGO_BAY)


INDEX_TO_TILE = tuple(list(TileType))


@dataclass(frozen=True)
class Tileset:
    """Tileset groups the tiles and provides the mappings for tile types.

    Attributes:
        tileset_index - start index of all tiles from the tileset
    """
    tileset_index: int

    @property
    def first_tile_index(self) -> int:
        """The index of the first tile of the tileset."""
        return self.tileset_index * len(TileType)

    def tile_of(self, tile_index: int) -> TileType:
        """The type of tile with given tile index (which is specific to the tileset)

        :param tile_index: tile index to find tile type for
        :return: type of tile for given tile index in tileset
        """
        num_tiles = len(TileType)
        index_in_range = self.first_tile_index <= tile_index < self.first_tile_index + num_tiles
        return INDEX_TO_TILE[tile_index % num_tiles] if index_in_range else TileType.VOID
