from enum import Enum

class GameState(Enum):
    QUIT = -1
    MAIN_MENU = 0
    GAME_SELECT = 1
    LOGIC_GATE = 2
    ALGORITHM = 3
    NUMBER_CONVERTER = 4
    OPTIONS = 5