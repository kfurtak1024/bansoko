from typing import List

import pyxel

from bansoko.game.level import LevelStatistics, Level, LevelTemplate, NUM_LEVELS, LEVEL_SIZE, TILE_SIZE, TilePosition
from bansoko.game.screens.choose_level import ChooseLevelScreen
from bansoko.game.screens.game import GameScreen
from bansoko.game.screens.game_paused import GamePausedScreen
from bansoko.game.screens.level_completed import LevelCompletedScreen
from bansoko.game.screens.main_menu import MainMenuScreen
from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.gui.screen import Screen


class GameContext(ScreenFactory):
    level_templates: List[LevelTemplate]

    def __init__(self):
        self.level_templates = [self.__get_level_template(level) for level in range(NUM_LEVELS)]

    def get_main_menu(self) -> Screen:
        return MainMenuScreen(self)

    def get_game_screen(self, level: int) -> Screen:
        return GameScreen(self, Level(self.level_templates[level]))

    def get_choose_level_screen(self) -> Screen:
        return ChooseLevelScreen(self)

    def get_game_paused_screen(self, level: int) -> Screen:
        return GamePausedScreen(self, level)

    def get_level_completed_screen(self, level_stats: LevelStatistics) -> Screen:
        return LevelCompletedScreen(self, level_stats)

    def __get_level_template(self, level_num: int) -> LevelTemplate:
        tile_map = pyxel.tilemap(0)
        # tile_map_u and tile_map_v should become part of LevelTemplate
        tile_map_u = LEVEL_SIZE * (level_num % TILE_SIZE)
        tile_map_v = LEVEL_SIZE * (level_num // TILE_SIZE)
        player_start = None
        crates = []
        for u in range(tile_map_u, tile_map_u + LEVEL_SIZE):
            for v in range(tile_map_v, tile_map_v + LEVEL_SIZE):
                tile = tile_map.get(u, v)
                position = TilePosition(u - tile_map_u, v - tile_map_v)
                if self.__is_crate_tile(tile):
                    crates.append(position)
                elif self.__is_player_start_tile(tile):
                    player_start = position

        return LevelTemplate(level_num, player_start, crates)

    @staticmethod
    def __is_crate_tile(tile: int):
        # TODO: Read it from resources file (instead of hard-coded value)
        return tile in [4, 5]

    @staticmethod
    def __is_player_start_tile(tile: int):
        # TODO: Read it from resources file (instead of hard-coded value)
        return tile == 2
