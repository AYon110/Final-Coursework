import pygame
import pygame.freetype

WHITE = (255,255,255)
BLUE = (59, 126, 209)


class Screen:
    def __init__(self, screen_surface):
        self.screen = screen_surface
        self.elements = []

    def handle_events(self, events):
        mouse_up = False
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True
        mouse_pos = pygame.mouse.get_pos()
        for element in self.elements:
            action = element.update(mouse_pos, mouse_up)
            if action:
                return action
        return None

    def draw(self):
        self.screen.fill(BLUE)
        for element in self.elements:
            element.draw(self.screen)
        pygame.display.flip()