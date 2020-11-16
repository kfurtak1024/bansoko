"""Module defining game screen containing information on how to play."""

from bansoko.game.screens.screen_factory import ScreenFactory
from bansoko.graphics import Point
from bansoko.graphics.text import draw_text
from bansoko.gui.menu import MenuScreen, TextMenuItem, Menu


class TutorialScreen(MenuScreen):
    """Screen displayed before player starts tutorial level.

    Player can only go back to playfield screen from here.
    """

    def __init__(self, screen_factory: ScreenFactory):
        bundle = screen_factory.get_bundle()
        menu = Menu.with_defaults(tuple([
            TextMenuItem("OK", lambda: None)
        ]), position=Point(120, 179))
        super().__init__(
            menu=menu, allow_going_back=True, background=bundle.get_background("tutorial"),
            semi_transparent=True)

    def draw(self, draw_as_secondary: bool = False) -> None:
        super().draw(draw_as_secondary)
        # TODO: Those should belong to resources file!
        draw_text(Point(32, 48), "WELCOME TO BANSOKO!\n\n"
                                 "WE ARE SCAVENGERS, WE COLLECT CARGOS THAT PEOPLE\n"
                                 "HAVE LEFT IN ABANDONED SHIPS IN DEEP SPACE.\n"
                                 "IT'S A DANGEROUS JOB. THAT'S WHY WE USE ROBOTS.")
        draw_text(Point(32, 82), "#7YOU CONTROL YOUR ROBOT BY USING ARROW KEYS:")
        draw_text(Point(32, 106), "#7YOUR GOAL IS TO PUSH ALL CRATES TO CARGO BAYS:")
        draw_text(Point(108, 118), "#7REMEMBER, YOU CAN ONLY #BPUSH\n"
                                   "#7CRATES (YOU CANNOT PULL THEM)")
        draw_text(Point(32, 136), "#7IF YOU MAKE A MISTAKE YOU CAN #BUNDO #7YOUR MOVE\n"
                                  "BY PRESSING:")
        draw_text(Point(32, 167), "#7NOTE, YOU CAN #BUNDO #7AS MANY MOVES AS YOU NEED.")
