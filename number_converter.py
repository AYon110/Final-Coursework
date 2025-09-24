import pygame
import pygame.freetype
import random
from ui_element import UIelement
from game_state import GameState
from screen_base import Screen

WHITE = (255, 255, 255)
BLUE = (59, 126, 209)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

pygame.freetype.init()
FONT = pygame.freetype.SysFont("Courier", 30, bold=True)

NUMBER_SYSTEMS = ["denary", "binary", "hex"]


def generate_question():
    input_type = random.choice(NUMBER_SYSTEMS)
    output_type = random.choice([ns for ns in NUMBER_SYSTEMS if ns != input_type])
    number = random.randint(0, 255)

    if input_type == "denary":
        input_value = str(number)
    elif input_type == "binary":
        input_value = bin(number)[2:]
    else:  # hex
        input_value = hex(number)[2:].upper()

    if output_type == "denary":
        correct_answer = str(number)
    elif output_type == "binary":
        correct_answer = bin(number)[2:]
    else:  # hex
        correct_answer = hex(number)[2:].upper()

    question_text = f"Convert {input_value} ({input_type}) to {output_type}:"
    return question_text, correct_answer


# --------------------------
# Input Box
# --------------------------
class InputBox:
    def __init__(self, x, y, w, h, placeholder=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WHITE
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.font = pygame.freetype.SysFont("Courier", 25)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active if clicked inside box
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
        return None

    def draw(self, screen):
        # Draw rectangle
        pygame.draw.rect(screen, self.color, self.rect, 2)
        # Draw text or placeholder
        display_text = self.text if self.text else self.placeholder
        self.font.render_to(screen, (self.rect.x+5, self.rect.y+10), display_text, WHITE)




# --------------------------
# Converter Screen
# --------------------------
class ConverterScreen(Screen):
    def __init__(self, screen_surface):
        super().__init__(screen_surface)
        self.back_button = UIelement((100, 550), "Back", 25, WHITE, BLUE, action=GameState.GAME_SELECT)
        self.input_box = InputBox(250, 300, 300, 50)
        self.reset_game()
        self.elements = [self.back_button]
        self.feedback_time = 0  # store when feedback was set

    def reset_game(self):
        self.question_text, self.correct_answer = generate_question()
        self.feedback = ""
        self.feedback_time = 0

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_up = False
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_up = True

            # Pass events to input box
            answer = self.input_box.handle_event(event)
            if answer is not None:
                if answer.strip().upper() == self.correct_answer.upper():
                    self.feedback = "Correct!"
                else:
                    self.feedback = f"Wrong! Correct: {self.correct_answer}"
                self.feedback_time = pygame.time.get_ticks()  # mark time
                self.question_text, self.correct_answer = generate_question()

        # Handle back button
        action = self.back_button.update(mouse_pos, mouse_up)
        if action:
            self.reset_game()  # wipe old question + feedback
            return action

        return None

    def draw(self):
        self.screen.fill(BLUE)
        # Question text
        FONT.render_to(self.screen, (100, 200), self.question_text, WHITE)
        # Input box
        self.input_box.draw(self.screen)

        # Feedback (centered below input box, auto-clears after 3 sec)
        if self.feedback:
            if pygame.time.get_ticks() - self.feedback_time < 3000:  # 3 seconds
                feedback_surface, _ = FONT.render(
                    self.feedback,
                    GREEN if "Correct" in self.feedback else RED
                )
                feedback_rect = feedback_surface.get_rect(center=(400, 380))
                self.screen.blit(feedback_surface, feedback_rect)
            else:
                self.feedback = ""  # clear feedback

        # Buttons
        for element in self.elements:
            element.draw(self.screen)
        pygame.display.flip()




















