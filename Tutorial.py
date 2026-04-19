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
FONT = pygame.freetype.SysFont("Courier", 16, bold=True)


class TutorialScreen(Screen):
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
        return action


    def draw(self):
        self.screen.fill(BLUE)

        FONT.render_to(self.screen, (50, 40), "Tutorial", WHITE)

        FONT.render_to(self.screen, (50, 80), "Logic Gates Simulator", WHITE)
        FONT.render_to(self.screen, (70, 120), "1. Select a component from the palette on the left.", WHITE)
        FONT.render_to(self.screen, (70, 150), "2. Click on the canvas to place the component.", WHITE)
        FONT.render_to(self.screen, (70, 190), "3. Click an output pin, then an input pin, to create a wire.", WHITE)
        FONT.render_to(self.screen, (70, 210), "4. Click a switch to toggle its state between 0 and 1.", WHITE)
        FONT.render_to(self.screen, (70, 240),
                       "5. Drag components to move them or place them over the bin to delete them.", WHITE)
        FONT.render_to(self.screen, (70, 270), "6. The bulb will light up when the circuit output is 1.", WHITE)

        FONT.render_to(self.screen, (50, 330), "Number Converter .. (Use least number of bits for binary)", WHITE)
        FONT.render_to(self.screen, (70, 370), "1. Enter your name to start the game.", WHITE)
        FONT.render_to(self.screen, (70, 400), "2. Read the conversion question shown on screen.", WHITE)
        FONT.render_to(self.screen, (70, 430), "3. Type your answer into the input box and press Enter.", WHITE)
        FONT.render_to(self.screen, (70, 460), "4. If your answer is correct, your score increases.", WHITE)
        FONT.render_to(self.screen, (70, 490),
                       "5. If your answer is wrong,correct answer is shown and your streak resets.", WHITE)

        FONT.render_to(self.screen, (50, 520),
                       "The Algorithm Simulator already includes its own on-screen instructions.", WHITE)


        for element in self.elements:
            element.draw(self.screen)
        pygame.display.flip()



