import pygame
import pygame.freetype
import random
from ui_element import UIelement
from game_state import GameState
from screen_base import Screen
import sys




WHITE = (255, 255, 255)
BLUE = (59, 126, 209)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

pygame.freetype.init()
FONT = pygame.freetype.SysFont("Courier", 30, bold=True)


class OptionsScreen(Screen):
    def __init__(self, screen_surface):
        super().__init__(screen_surface)
        self.back_button = UIelement((100,550), "Back", 25, WHITE, BLUE, action=GameState.MAIN_MENU)
        self.elements = [self.back_button]

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_up = False
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_up = True
        action = self.back_button.update(mouse_pos, mouse_up)


    def draw(self):
        self.screen.fill(BLUE)


        for element in self.elements:
            element.draw(self.screen)
        pygame.display.flip()



