import pygame
import pygame.freetype
from game_state import GameState
import sys
from ui_element import UIelement
from screen_base import Screen
from logic_gates import LogicGateScreen
from algorithm_sim import AlgorithmScreen
from number_converter import ConverterScreen

WHITE = (255,255,255)
BLUE = (59, 126, 209)


# -----------------------------
# Main Menu Screen
# -----------------------------
class MainMenu(Screen):
    def __init__(self, screen_surface):
        super().__init__(screen_surface)
        self.elements = [
            UIelement((400, 300), "Get Started", 30, WHITE, BLUE, action=GameState.GAME_SELECT),
            UIelement((400, 400), "Options", 25, WHITE, BLUE),
            UIelement((400, 450), "Quit", 25, WHITE, BLUE, action=GameState.QUIT)
        ]

# -----------------------------
# Game Selection Screen
# -----------------------------
class GameSelect(Screen):
    def __init__(self, screen_surface):
        super().__init__(screen_surface)
        self.elements = [
            UIelement((400, 250), "Logic Gates", 30, WHITE, BLUE, action=GameState.LOGIC_GATE),
            UIelement((400, 350), "Algorithm Simulator", 30, WHITE, BLUE, action=GameState.ALGORITHM),
            UIelement((400, 450), "Number Converter", 30, WHITE, BLUE, action=GameState.NUMBER_CONVERTER),
            UIelement((400, 550), "Back", 25, WHITE, BLUE, action=GameState.MAIN_MENU)
        ]

# -----------------------------
# Main Application
# -----------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    screens = {
        GameState.MAIN_MENU: MainMenu(screen),
        GameState.GAME_SELECT: GameSelect(screen),
        GameState.LOGIC_GATE: LogicGateScreen(screen),
        GameState.ALGORITHM: AlgorithmScreen(screen),
        GameState.NUMBER_CONVERTER: ConverterScreen(screen)
    }

    current_state = GameState.MAIN_MENU

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        action = screens[current_state].handle_events(events)

        if action == GameState.QUIT:
            pygame.quit()
            sys.exit()
        elif action in screens:
            current_state = action

        screens[current_state].draw()
        clock.tick(60)

main()
