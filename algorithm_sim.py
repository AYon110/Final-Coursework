# algorithm_sim.py
import random
import pygame
import pygame.freetype

from ui_element import UIelement
from screen_base import Screen
from game_state import GameState

# --- Colors ---
WHITE = (255, 255, 255)
BLUE = (59, 126, 209)
BLACK = (0, 0, 0)
GREY = (120, 120, 120)
LIGHT = (200, 200, 200)
YELLOW = (255, 230, 50)
GREEN = (0, 200, 0)
RED = (220, 50, 50)
CYAN = (80, 220, 220)
MAGENTA = (220, 80, 220)

pygame.freetype.init()
FONT = pygame.freetype.SysFont("Courier", 22, bold=True)
FONT_SM = pygame.freetype.SysFont("Courier", 18, bold=True)

BOX_W, BOX_H = 60, 60
SPACING = 10
START_X = 60
ROW_Y = 320


# -----------------------
# Step Generators
# -----------------------
def generate_binary_search_steps(arr, target):
    steps = []
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        steps.append({
            "arr": arr[:],
            "low": low,
            "high": high,
            "mid": mid,
            "cmp": (arr[mid] > target) - (arr[mid] < target)
        })
        if arr[mid] == target:
            break
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return steps


def generate_bubble_sort_steps(arr):
    steps = []
    a = arr[:]
    n = len(a)
    swapped_any = True
    pass_num = 0
    while swapped_any:
        swapped_any = False
        for j in range(0, n - 1 - pass_num):
            step = {"arr": a[:], "i": j, "j": j + 1, "swapped": False}
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                step["swapped"] = True
                swapped_any = True
            steps.append(step)
        pass_num += 1
    steps.append({"arr": a[:], "i": None, "j": None, "swapped": False, "done": True})
    return steps


# -----------------------
# Screen
# -----------------------
class AlgorithmScreen(Screen):
    def __init__(self, screen_surface):
        super().__init__(screen_surface)

        # Navigation
        self.back_button = UIelement((100, 550), "Back", 25, WHITE, BLUE, action=GameState.GAME_SELECT)

        # Row 1 (top toolbar): mode + generate
        self.mode_bin_btn = UIelement((160, 90), "Binary Search", 22, WHITE, BLUE, action="MODE_BIN")
        self.mode_bub_btn = UIelement((360, 90), "Bubble Sort", 22, WHITE, BLUE, action="MODE_BUBBLE")
        self.generate_btn = UIelement((650, 90), "Generate", 22, WHITE, BLUE, action="GEN")

        # Row 2 (BIN only): target picker (no overlaps)
        self.target_left  = UIelement((460, 140), "◀", 22, WHITE, BLUE, action="TGT_LEFT")
        self.target_right = UIelement((740, 140), "▶", 22, WHITE, BLUE, action="TGT_RIGHT")
        # Clickable "Target: <val>" pill in the middle:
        self.target_rect = pygame.Rect(560, 126, 160, 28)  # draw + detect manually

        # Bottom row: controls
        self.reset_btn    = UIelement((350, 500), "Reset", 22, WHITE, BLUE, action="RESET")
        self.start_btn    = UIelement((460, 500), "Start", 22, WHITE, BLUE, action="START")
        self.prev_btn     = UIelement((570, 500), "Prev", 22, WHITE, BLUE, action="PREV")
        self.next_btn     = UIelement((680, 500), "Next", 22, WHITE, BLUE, action="NEXT")

        # Only the back button is auto-managed by Screen
        self.elements = [self.back_button]

        # State
        self.mode = "BIN"          # "BIN" or "BUBBLE"
        self.arr = []              # working array (sorted for BIN)
        self.source_arr = []       # original (for bubble)
        self.target_idx = 0
        self.target_val = None
        self.steps = []
        self.step_i = -1
        self.error_msg = ""
        self.regen_on_next_entry = False  # when you come back to this screen, make a fresh list

    # ------------- helpers -------------
    def _random_list(self, n=10, low=1, high=99):
        return random.sample(range(low, high + 1), n)

    def _update_manual_buttons(self, mouse_pos, mouse_up):
        # Row 1 (always)
        for b in [self.mode_bin_btn, self.mode_bub_btn, self.generate_btn]:
            b.update(mouse_pos, mouse_up)
        # Row 2 (only BIN mode)
        if self.mode == "BIN":
            for b in [self.target_left, self.target_right]:
                b.update(mouse_pos, mouse_up)
        # Bottom row (always)
        for b in [self.reset_btn, self.start_btn, self.prev_btn, self.next_btn]:
            b.update(mouse_pos, mouse_up)

    def _click_action(self, mouse_pos, mouse_up):
        # Back
        action = self.back_button.update(mouse_pos, mouse_up)
        if action:
            # mark to regenerate when this screen is next shown
            self.regen_on_next_entry = True
            return action

        # Top toolbar & bottom controls
        for b in [self.mode_bin_btn, self.mode_bub_btn, self.generate_btn,
                  self.reset_btn, self.start_btn, self.prev_btn, self.next_btn]:
            act = b.update(mouse_pos, mouse_up)
            if act:
                return act

        # BIN-only target controls (arrows)
        if self.mode == "BIN":
            for b in [self.target_left, self.target_right]:
                act = b.update(mouse_pos, mouse_up)
                if act:
                    return act

            # Clickable target pill
            if mouse_up and self.target_rect.collidepoint(mouse_pos):
                return "TGT_RIGHT"  # simple: clicking cycles to the next value

        return None

    def _set_mode(self, new_mode):
        self.mode = new_mode
        self.error_msg = ""
        self.steps = []
        self.step_i = -1
        self.target_val = None
        self.target_idx = 0
        if self.mode == "BIN":
            self.source_arr = self._random_list()
            self.arr = sorted(self.source_arr)
            self.target_idx = 0
            self.target_val = self.arr[self.target_idx]
        else:
            self.arr = self._random_list()
            self.source_arr = self.arr[:]

    def _ensure_generated(self):
        if not self.arr:
            if self.mode == "BIN":
                self.source_arr = self._random_list()
                self.arr = sorted(self.source_arr)
                self.target_idx = 0
                self.target_val = self.arr[self.target_idx]
            else:
                self.arr = self._random_list()
                self.source_arr = self.arr[:]

    # ------------- event loop -------------
    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_up = any(e.type == pygame.MOUSEBUTTONUP and e.button == 1 for e in events)

        # If we were marked to regenerate (because user exited earlier), do it once on entry
        if self.regen_on_next_entry:
            self._set_mode(self.mode)  # regenerates appropriate list for current mode
            self.regen_on_next_entry = False

        # keep hover states fresh
        self._update_manual_buttons(mouse_pos, mouse_up)

        # which control fired?
        act = self._click_action(mouse_pos, mouse_up)
        if act == GameState.GAME_SELECT:
            return act

        if act == "MODE_BIN":
            self._set_mode("BIN")
        elif act == "MODE_BUBBLE":
            self._set_mode("BUBBLE")
        elif act == "GEN":
            self._ensure_generated()
            self.steps = []
            self.step_i = -1
            self.error_msg = ""
            if self.mode == "BIN":
                self.target_idx = 0
                self.target_val = self.arr[self.target_idx]
        elif act == "TGT_LEFT" and self.mode == "BIN":
            if self.arr:
                self.target_idx = (self.target_idx - 1) % len(self.arr)
                self.target_val = self.arr[self.target_idx]
        elif act == "TGT_RIGHT" and self.mode == "BIN":
            if self.arr:
                self.target_idx = (self.target_idx + 1) % len(self.arr)
                self.target_val = self.arr[self.target_idx]
        elif act == "START":
            self._ensure_generated()
            if self.mode == "BIN":
                if self.target_val is None:
                    self.error_msg = "Choose a target first."
                    return None
                self.steps = generate_binary_search_steps(self.arr, self.target_val)
                self.step_i = 0 if self.steps else -1
                self.error_msg = "" if self.steps else "No steps generated."
            else:
                self.steps = generate_bubble_sort_steps(self.source_arr)
                self.step_i = 0 if self.steps else -1
                self.error_msg = "" if self.steps else "No steps generated."
        elif act == "PREV":
            if self.steps:
                self.step_i = max(0, self.step_i - 1)
        elif act == "NEXT":
            if self.steps:
                self.step_i = min(len(self.steps) - 1, self.step_i + 1)
        elif act == "RESET":
            self.steps = []
            self.step_i = -1
            self.error_msg = ""

        return None

    # ------------- drawing -------------
    def _draw_header(self):
        # Title + mode
        FONT.render_to(self.screen, (20, 20), "Algorithm Visualiser", WHITE)
        mode_str = "Mode: Binary Search" if self.mode == "BIN" else "Mode: Bubble Sort"
        FONT_SM.render_to(self.screen, (20, 50), mode_str, WHITE)

        # Row 1: toolbar
        for b in [self.mode_bin_btn, self.mode_bub_btn, self.generate_btn]:
            b.draw(self.screen)

        # Row 2: BIN-only target picker (no overlap)
        if self.mode == "BIN":
            FONT_SM.render_to(self.screen, (20, 140), "Pick target (click pill or use ◀ ▶):", WHITE)
            self.target_left.draw(self.screen)

            # Target pill (clickable)
            pygame.draw.rect(self.screen, CYAN, self.target_rect, border_radius=6)
            pygame.draw.rect(self.screen, WHITE, self.target_rect, 2, border_radius=6)
            t = "-" if self.target_val is None else str(self.target_val)
            label = f"Target: {t}"
            txt, _ = FONT_SM.render(label, BLACK)
            self.screen.blit(txt, txt.get_rect(center=self.target_rect.center))

            self.target_right.draw(self.screen)

    def _draw_controls(self):
        # Bottom controls
        for b in [self.reset_btn, self.start_btn, self.prev_btn, self.next_btn]:
            b.draw(self.screen)

        if self.steps:
            info = f"Step {self.step_i + 1} / {len(self.steps)}"
            FONT_SM.render_to(self.screen, (50, 510), info, WHITE)

        if self.error_msg:
            FONT_SM.render_to(self.screen, (50, 90), self.error_msg, RED)

    def _draw_array_boxes(self, arr, highlight=None):
        y = ROW_Y
        for i, num in enumerate(arr):
            x = START_X + i * (BOX_W + SPACING)
            rect = pygame.Rect(x, y, BOX_W, BOX_H)

            color = WHITE
            if highlight:
                if "low" in highlight:  # binary
                    if i < highlight["low"] or i > highlight["high"]:
                        color = GREY
                    if i == highlight.get("mid"):
                        color = YELLOW
                if "i" in highlight:    # bubble
                    if i == highlight["i"]:
                        color = CYAN
                    if i == highlight["j"]:
                        color = MAGENTA
                    if highlight.get("swapped"):
                        pygame.draw.rect(self.screen, GREEN, rect.inflate(6, 6), 3, border_radius=8)

            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            text_surface, _ = FONT.render(str(num), BLACK)
            self.screen.blit(text_surface, text_surface.get_rect(center=rect.center))

    def draw(self):
        self.screen.fill(BLUE)

        # Header + toolbars
        self._draw_header()

        # Data area
        if not self.steps:
            arr = self.arr if self.mode == "BIN" else (self.source_arr if self.source_arr else self.arr)
            if arr:
                self._draw_array_boxes(arr, highlight=None)
                if self.mode == "BIN":
                    FONT_SM.render_to(self.screen, (50, 290), "Array is sorted for binary search.", LIGHT)
            else:
                FONT_SM.render_to(self.screen, (50, 290), "Click Generate to create a list.", LIGHT)
        else:
            s = self.steps[self.step_i]
            if self.mode == "BIN":
                self._draw_array_boxes(
                    s["arr"], highlight={"low": s["low"], "high": s["high"], "mid": s["mid"]}
                )
                cmp_val = s["cmp"]
                msg = "Comparing target with mid: "
                if cmp_val == 0:
                    msg += "EQUAL"
                elif cmp_val < 0:
                    msg += "TARGET < MID → search left"
                else:
                    msg += "TARGET > MID → search right"
                FONT_SM.render_to(self.screen, (50, 290), msg, WHITE)
                FONT_SM.render_to(self.screen, (50, 270), f"Target = {self.target_val}", CYAN)
            else:
                self._draw_array_boxes(
                    s["arr"],
                    highlight={"i": s.get("i"), "j": s.get("j"), "swapped": s.get("swapped", False)}
                )
                if s.get("done"):
                    FONT_SM.render_to(self.screen, (50, 290), "Sorted ✅", GREEN)
                else:
                    msg = "Comparing indices i, j"
                    if s.get("swapped"):
                        msg += " — swapped!"
                    FONT_SM.render_to(self.screen, (50, 290), msg, WHITE)

        # Bottom controls + back
        self._draw_controls()
        self.back_button.draw(self.screen)

        pygame.display.flip()
