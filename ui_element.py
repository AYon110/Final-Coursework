import pygame
import pygame.freetype
from pygame.sprite import Sprite


WHITE = (255,255,255)
BLUE = (59, 126, 209)


def create_text_metadata(text, font_size, text_color, bg_color):
    font = pygame.freetype.SysFont("Courier", font_size, bold = True)
    surface,_ = font.render(text = text, fgcolor = text_color, bgcolor = bg_color)
    return surface.convert_alpha()


class UIelement(Sprite):

    def __init__(self, center_pos, text, font_size, text_color, bg_color, action = None):

        super().__init__()
        self.mouse_over = False
        self.action = action
        default_image = create_text_metadata(text, font_size, text_color, bg_color)
        highlighted_image = create_text_metadata(text, font_size * 1.2, text_color, bg_color)
        self.images = [default_image, highlighted_image]
        self.rects = [
            default_image.get_rect(center = center_pos),
            highlighted_image.get_rect(center = center_pos)]

    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

    def update(self, mouse_pos, mouse_up):
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)