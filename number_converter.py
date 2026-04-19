import pygame
import pygame.freetype
import random
from ui_element import UIelement
from game_state import GameState
from screen_base import Screen
import json
import os

WHITE = (255, 255, 255)
BLUE = (59, 126, 209)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

pygame.freetype.init()
FONT = pygame.freetype.SysFont("Courier", 30, bold=True)

NUMBER_SYSTEMS = ["denary", "binary", "hex"]

SCORES_FILE = "scores.json"


def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []

    try:
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_score(name, score):
    scores = load_scores()

    found = False
    for entry in scores:
        if entry["name"].lower() == name.lower():
            if score > entry["score"]:
                entry["score"] = score
            found = True
            break

    if not found:
        scores.append({"name": name, "score": score})

    scores.sort(key=lambda x: x["score"], reverse=True)

    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=4)


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



# Input Box

class InputBox:
    def __init__(self, x, y, w, h, placeholder=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WHITE
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.font = pygame.freetype.SysFont("Courier", 25)


    def clear(self):
        self.text = ""


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





# Converter Screen

class ConverterScreen(Screen):
    def __init__(self, screen_surface):
        super().__init__(screen_surface)

        self.back_button = UIelement((100, 550), "Back", 25, WHITE, BLUE, action=GameState.GAME_SELECT)
        self.scores_button = UIelement((650, 550), "Scores", 25, WHITE, BLUE, action="SHOW_SCORES")

        self.name_box = InputBox(250, 150, 300, 50, placeholder="")
        self.answer_box = InputBox(250, 300, 300, 50, placeholder="")

        self.player_name = ""
        self.score = 0
        self.show_scores = False
        self.leaderboard = load_scores()

        self.reset_game()
        self.elements = [self.back_button, self.scores_button]
        self.feedback_time = 0

    def reset_game(self):
        self.question_text, self.correct_answer = generate_question()
        self.feedback = ""
        self.feedback_time = 0

    def save_current_score(self):
        if self.player_name.strip():
            save_score(self.player_name.strip(), self.score)
            self.leaderboard = load_scores()

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_up = False

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_up = True

            # If no name yet, use name box first
            if not self.player_name:
                entered_name = self.name_box.handle_event(event)
                if entered_name is not None:
                    entered_name = entered_name.strip()
                    if entered_name:
                        self.player_name = entered_name
                        self.name_box.active = False
            else:
                # Once name is entered, use answer box
                answer = self.answer_box.handle_event(event)
                if answer is not None:
                    if answer.strip().upper() == self.correct_answer.upper():
                        self.feedback = "Correct!"
                        self.score += 1
                    else:
                        self.feedback = f"Wrong! Correct: {self.correct_answer}"

                        # save streak before resetting
                        if self.player_name.strip() and self.score > 0:
                            save_score(self.player_name.strip(), self.score)
                            self.leaderboard = load_scores()

                        self.score = 0  # reset streak after wrong answer

                    self.feedback_time = pygame.time.get_ticks()
                    self.answer_box.clear()
                    self.question_text, self.correct_answer = generate_question()

        # Handle buttons
        action = self.back_button.update(mouse_pos, mouse_up)
        if action:
            self.save_current_score()
            self.score = 0
            self.player_name = ""
            self.name_box.clear()
            self.answer_box.clear()
            self.reset_game()
            return action

        score_action = self.scores_button.update(mouse_pos, mouse_up)
        if score_action == "SHOW_SCORES":
            self.show_scores = not self.show_scores
            self.leaderboard = load_scores()

        return None

    def draw(self):
        self.screen.fill(BLUE)

        # Name section
        if not self.player_name:
            FONT.render_to(self.screen, (180, 100), "Enter your name to start:", WHITE)
            self.name_box.draw(self.screen)
        else:
            FONT.render_to(self.screen, (100, 100), f"Player: {self.player_name}", WHITE)
            FONT.render_to(self.screen, (500, 100), f"Score: {self.score}", WHITE)

            # Question text
            FONT.render_to(self.screen, (100, 200), self.question_text, WHITE)

            # Answer input
            self.answer_box.draw(self.screen)

            # Feedback
            if self.feedback:
                if pygame.time.get_ticks() - self.feedback_time < 3000:
                    feedback_surface, _ = FONT.render(
                        self.feedback,
                        GREEN if "Correct" in self.feedback else RED
                    )
                    feedback_rect = feedback_surface.get_rect(center=(400, 380))
                    self.screen.blit(feedback_surface, feedback_rect)
                else:
                    self.feedback = ""

        # Draw leaderboard panel
        if self.show_scores:
            pygame.draw.rect(self.screen, (20, 20, 20), (180, 120, 440, 350))
            pygame.draw.rect(self.screen, WHITE, (180, 120, 440, 350), 2)
            FONT.render_to(self.screen, (300, 140), "Leaderboard", WHITE)

            top_scores = self.leaderboard[:10]
            y = 190
            for i, entry in enumerate(top_scores, start=1):
                line = f"{i}. {entry['name']} - {entry['score']}"
                FONT.render_to(self.screen, (220, y), line, WHITE)
                y += 30

            if not top_scores:
                FONT.render_to(self.screen, (250, 220), "No scores yet", WHITE)

        # Buttons
        for element in self.elements:
            element.draw(self.screen)

        pygame.display.flip()




















