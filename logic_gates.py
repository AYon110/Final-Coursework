# logic_gates.py
import pygame
import pygame.freetype
from screen_base import Screen
from game_state import GameState
from ui_element import UIelement

# ---------- Colors ----------
WHITE = (255, 255, 255)
BLUE = (59, 126, 209)
BLACK = (0, 0, 0)
GREY = (140, 140, 140)
LIGHT_GREY = (190, 190, 190)
YELLOW = (255, 214, 10)
GREEN = (0, 200, 0)
RED = (220, 50, 50)
PALETTE_BG = (30, 60, 100)
GRID_LINE = (70, 100, 140)
SELECT_C = (255, 170, 50)

pygame.freetype.init()
FONT = pygame.freetype.SysFont("Courier", 18, bold=True)

# ---------- Layout ----------
WIDTH, HEIGHT = 800, 600
PALETTE_W = 180
GRID_SIZE = 50
CANVAS_X0 = PALETTE_W
CANVAS_RECT = pygame.Rect(CANVAS_X0, 0, WIDTH - CANVAS_X0, HEIGHT)

# Pins / wiring
PIN_RADIUS = 9                # bigger pin visuals
PIN_HIT_R = 18                # hover/click radius
CONNECT_MAX_DIST = 24         # snap distance for finishing a wire

def snap_to_grid(x, y):
    gx = CANVAS_X0 + ((x - CANVAS_X0) // GRID_SIZE) * GRID_SIZE
    gy = (y // GRID_SIZE) * GRID_SIZE
    return int(gx), int(gy)

def dist(a, b):
    return ((a[0]-b[0])**2 + (a[1]-b[1])**2) ** 0.5

def point_segment_distance(p, a, b):
    # distance from point p to line segment ab
    (px, py), (ax, ay), (bx, by) = p, a, b
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    ab_len2 = abx*abx + aby*aby
    t = 0 if ab_len2 == 0 else max(0, min(1, (apx*abx + apy*aby) / ab_len2))
    cx, cy = ax + t * abx, ay + t * aby
    return ((px - cx)**2 + (py - cy)**2) ** 0.5


# ---------- Base Component ----------
class Component:
    def __init__(self, x, y, w=100, h=60, label="COMP", num_inputs=0, num_outputs=1):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.inputs = [0] * num_inputs
        self.output = 0
        self.selected = False

    def get_input_pins(self):
        if self.num_inputs == 0:
            return []
        pins = []
        base_y = self.rect.centery
        spacing = 20
        offset = (self.num_inputs - 1) * spacing / 2
        for i in range(self.num_inputs):
            pins.append((self.rect.left, int(base_y - offset + i * spacing)))
        return pins

    def get_output_pins(self):
        return [(self.rect.right, self.rect.centery)] if self.num_outputs else []

    def compute(self):
        pass

    def draw_frame(self, screen):
        color = SELECT_C if self.selected else WHITE
        pygame.draw.rect(screen, color, self.rect, 2, border_radius=8)
        FONT.render_to(
            screen,
            (self.rect.centerx - 8 * len(self.label) // 2, self.rect.centery - 8),
            self.label,
            WHITE
        )


# ---------- Specific Components ----------
class Switch(Component):
    def __init__(self, x, y):
        super().__init__(x, y, label="SWITCH", num_inputs=0, num_outputs=1)
        self.state = 0

    def toggle(self):
        self.state = 1 - self.state

    def compute(self):
        self.output = self.state

    def draw(self, screen):
        fill = LIGHT_GREY if self.state == 0 else (120, 180, 120)
        pygame.draw.rect(screen, fill, self.rect, border_radius=8)
        self.draw_frame(screen)
        FONT.render_to(screen, (self.rect.x + 8, self.rect.y + 8), f"OUT:{self.output}", BLACK)
        for p in self.get_output_pins():
            pygame.draw.circle(screen, GREEN, p, PIN_RADIUS)


class AndGate(Component):
    def __init__(self, x, y):
        super().__init__(x, y, label="AND", num_inputs=2, num_outputs=1)

    def compute(self):
        self.output = 1 if all(self.inputs) else 0

    def draw(self, screen):
        self.draw_frame(screen)


class OrGate(Component):
    def __init__(self, x, y):
        super().__init__(x, y, label="OR", num_inputs=2, num_outputs=1)

    def compute(self):
        self.output = 1 if any(self.inputs) else 0

    def draw(self, screen):
        self.draw_frame(screen)


class NotGate(Component):
    def __init__(self, x, y):
        super().__init__(x, y, label="NOT", num_inputs=1, num_outputs=1)

    def compute(self):
        self.output = 0 if (self.inputs and self.inputs[0] == 1) else 1

    def draw(self, screen):
        self.draw_frame(screen)


class Bulb(Component):
    def __init__(self, x, y):
        super().__init__(x, y, label="BULB", num_inputs=1, num_outputs=0)
        self.input_val = 0

    def compute(self):
        self.input_val = self.inputs[0] if self.inputs else 0

    def draw(self, screen):
        center = self.rect.center
        bulb_color = YELLOW if self.input_val else GREY
        pygame.draw.circle(screen, bulb_color, center, 28)
        pygame.draw.circle(screen, BLACK, center, 28, 2)
        FONT.render_to(screen, (center[0] - 18, center[1] - 42), "BULB", WHITE)
        # inputs
        for p in self.get_input_pins():
            pygame.draw.circle(screen, RED, p, PIN_RADIUS)


# ---------- Wire ----------
class Wire:
    def __init__(self, from_comp, from_pin_index, to_comp, to_pin_index):
        self.from_comp = from_comp
        self.from_pin_index = from_pin_index
        self.to_comp = to_comp
        self.to_pin_index = to_pin_index
        self.selected = False

    def get_points(self):
        sp = self.from_comp.get_output_pins()[self.from_pin_index]
        tp = self.to_comp.get_input_pins()[self.to_pin_index]
        return sp, tp

    def signal(self):
        return 1 if getattr(self.from_comp, "output", 0) else 0

    def draw(self, screen):
        sp, tp = self.get_points()
        sig = self.signal()
        color = YELLOW if sig else WHITE
        width = 5 if self.selected else 4
        pygame.draw.line(screen, color, sp, tp, width)


# ---------- Screen ----------
class LogicGateScreen(Screen):
    def __init__(self, screen_surface):
        super().__init__(screen_surface)

        self.back_button = UIelement((100, 550), "Back", 25, WHITE, BLUE, action=GameState.GAME_SELECT)

        # Palette (click to arm placement)
        self.palette = [
            ("SWITCH", pygame.Rect(20, 80,  PALETTE_W - 40, 40)),
            ("AND",    pygame.Rect(20, 140, PALETTE_W - 40, 40)),
            ("OR",     pygame.Rect(20, 200, PALETTE_W - 40, 40)),
            ("NOT",    pygame.Rect(20, 260, PALETTE_W - 40, 40)),
            ("BULB",   pygame.Rect(20, 320, PALETTE_W - 40, 40)),
            ("TRASH",  pygame.Rect(20, 420, PALETTE_W - 40, 40)),
        ]
        self.trash_rect = self.palette[-1][1]

        self.components = []
        self.bulb = None
        self.wires = []
        self.armed_type = None
        self.pending_from = None  # (component, out_idx)

        # selection/drag
        self.selected_comp = None
        self.selected_wire = None
        self.dragging = None
        self.drag_offset = (0, 0)

    # -------- helpers --------
    # -------- graph helpers --------
    def _build_graph(self):
        """
        Build adjacency and indegree maps based on current wires.
        - outgoing[comp] = list of (to_comp, to_pin_idx)
        - indegree[comp] = number of incoming wires
        - incoming_map[(to_comp, to_pin_idx)] = from_comp
        """
        outgoing = {c: [] for c in self.components}
        indegree = {c: 0 for c in self.components}
        incoming_map = {}

        for w in self.wires:
            frm = w.from_comp
            to  = w.to_comp
            pin = w.to_pin_index
            # one-wire-per-input already enforced when creating wires
            outgoing[frm].append((to, pin))
            indegree[to] += 1
            incoming_map[(to, pin)] = frm

        return outgoing, indegree, incoming_map

    def _reset_inputs(self):
        """Zero all gate inputs; reset bulb input display."""
        for c in self.components:
            if c.num_inputs:
                # keep exact input slot count
                c.inputs = [0] * c.num_inputs
            if isinstance(c, Bulb):
                c.input_val = 0

    def nearest_output_pin(self, pos, max_dist=PIN_HIT_R):
        best = None
        best_d = max_dist + 1
        for comp in self.components:
            for idx, pin in enumerate(comp.get_output_pins()):
                d = dist(pos, pin)
                if d <= max_dist and d < best_d:
                    best = (comp, idx)
                    best_d = d
        return best

    def nearest_input_pin(self, pos, max_dist=PIN_HIT_R):
        best = None
        best_d = max_dist + 1
        for comp in self.components:
            for idx, pin in enumerate(comp.get_input_pins()):
                d = dist(pos, pin)
                if d <= max_dist and d < best_d:
                    best = (comp, idx)
                    best_d = d
        return best

    def nearest_input_on_component(self, pos, comp):
        inputs = comp.get_input_pins()
        if not inputs:
            return None
        best_i, best_d = 0, 1e9
        for i, pin in enumerate(inputs):
            d = dist(pos, pin)
            if d < best_d:
                best_i, best_d = i, d
        return best_i

    def pick_component_rect(self, pos):
        for comp in reversed(self.components):
            if comp.rect.collidepoint(pos):
                return comp
        return None

    def wire_under_mouse(self, pos, threshold=10):
        # return first wire within threshold of mouse
        for w in reversed(self.wires):
            sp, tp = w.get_points()
            if point_segment_distance(pos, sp, tp) <= threshold:
                return w
        return None

    def place_component(self, comp_type, pos):
        x, y = snap_to_grid(*pos)
        if not CANVAS_RECT.collidepoint(x, y):
            return
        if comp_type == "SWITCH":
            self.components.append(Switch(x, y))
        elif comp_type == "AND":
            self.components.append(AndGate(x, y))
        elif comp_type == "OR":
            self.components.append(OrGate(x, y))
        elif comp_type == "NOT":
            self.components.append(NotGate(x, y))
        elif comp_type == "BULB":
            if self.bulb is None:
                self.bulb = Bulb(x, y)
                self.components.append(self.bulb)

    def remove_wires_connected_to(self, comp):
        self.wires = [
            w for w in self.wires
            if (w.from_comp is not comp) and (w.to_comp is not comp)
        ]

    def remove_existing_wire_to_input(self, target_comp, input_idx):
        self.wires = [w for w in self.wires if not (w.to_comp is target_comp and w.to_pin_index == input_idx)]

    def clear_selection(self):
        if self.selected_comp:
            self.selected_comp.selected = False
        if self.selected_wire:
            self.selected_wire.selected = False
        self.selected_comp = None
        self.selected_wire = None

    # -------- events --------
    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_up = False

        for e in events:
            # Cancel wiring via ESC
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.pending_from = None
                continue

            # Delete selected via DEL
            if e.type == pygame.KEYDOWN and e.key == pygame.K_DELETE:
                if self.selected_wire:
                    self.wires.remove(self.selected_wire)
                    self.selected_wire = None
                elif self.selected_comp:
                    if self.selected_comp is self.bulb:
                        self.bulb = None
                    self.remove_wires_connected_to(self.selected_comp)
                    self.components.remove(self.selected_comp)
                    self.selected_comp = None
                continue

            # --- Mouse down: start wire OR select/drag ---
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                # Start wire if output pin is under cursor
                out_hit = self.nearest_output_pin(e.pos, max_dist=PIN_HIT_R)
                if out_hit:
                    self.pending_from = out_hit
                    self.clear_selection()
                    self.dragging = None
                    continue

                # Select wire if clicked near it
                w = self.wire_under_mouse(e.pos, threshold=10)
                if w:
                    self.clear_selection()
                    self.selected_wire = w
                    w.selected = True
                    self.pending_from = None
                    self.dragging = None
                    continue

                # Select or start drag on component
                comp = self.pick_component_rect(e.pos)
                if comp and CANVAS_RECT.collidepoint(e.pos):
                    self.clear_selection()
                    self.selected_comp = comp
                    comp.selected = True
                    self.dragging = comp
                    self.drag_offset = (e.pos[0] - comp.rect.x, e.pos[1] - comp.rect.y)
                    self.pending_from = None
                    continue

                # Clicked canvas empty -> clear selection
                self.clear_selection()
                self.pending_from = None

            # Drag move
            if e.type == pygame.MOUSEMOTION and self.dragging:
                nx = e.pos[0] - self.drag_offset[0]
                ny = e.pos[1] - self.drag_offset[1]
                self.dragging.rect.topleft = (nx, ny)

            # Mouse up
            if e.type == pygame.MOUSEBUTTONUP:
                if e.button == 3:
                    # Right-click cancels wiring
                    self.pending_from = None
                    continue

                if e.button == 1:
                    mouse_up = True

                    # Palette clicks: arm placement
                    for label, rect in self.palette:
                        if rect.collidepoint(e.pos):
                            if label == "TRASH":
                                # arming trash doesn't make sense; it's a drop target
                                self.armed_type = None
                            else:
                                self.armed_type = label
                                self.pending_from = None
                            return None

                    # Place armed component
                    if self.armed_type and CANVAS_RECT.collidepoint(e.pos):
                        self.place_component(self.armed_type, e.pos)
                        self.armed_type = None
                        return None

                    # Finish drag -> snap; or delete if dropped on trash
                    if self.dragging:
                        if self.trash_rect.collidepoint(e.pos):
                            if self.dragging is self.bulb:
                                self.bulb = None
                            self.remove_wires_connected_to(self.dragging)
                            self.components.remove(self.dragging)
                            self.dragging = None
                            self.clear_selection()
                            return None
                        sx, sy = snap_to_grid(*self.dragging.rect.topleft)
                        self.dragging.rect.topleft = (sx, sy)
                        self.dragging = None

                    # Finish wiring (mouseup near input pin or gate body -> nearest input)
                    if self.pending_from is not None:
                        hit = self.nearest_input_pin(e.pos, max_dist=CONNECT_MAX_DIST)
                        if not hit:
                            gate_under = self.pick_component_rect(e.pos)
                            if gate_under:
                                idx = self.nearest_input_on_component(e.pos, gate_under)
                                if idx is not None:
                                    hit = (gate_under, idx)
                        if hit:
                            from_comp, out_idx = self.pending_from
                            to_comp, in_idx = hit
                            if from_comp is not to_comp and to_comp.num_inputs > in_idx:
                                # one wire per input
                                self.remove_existing_wire_to_input(to_comp, in_idx)
                                self.wires.append(Wire(from_comp, out_idx, to_comp, in_idx))
                        self.pending_from = None
                        continue

                    # Toggle switch (body only, not on pins)
                    comp = self.pick_component_rect(e.pos)
                    if comp and isinstance(comp, Switch):
                        if not self.nearest_output_pin(e.pos, max_dist=PIN_HIT_R) and not self.nearest_input_pin(e.pos, max_dist=PIN_HIT_R):
                            comp.toggle()
                            return None

        # Back button
        action = self.back_button.update(mouse_pos, mouse_up)
        if action:
            # clear state on exit
            self.components.clear()
            self.wires.clear()
            self.bulb = None
            self.armed_type = None
            self.pending_from = None
            self.clear_selection()
            return action

        return None

    # -------- simulation --------
    # -------- simulation (topological) --------
    def simulate(self):
        """
        Evaluate the circuit from sources to sinks using a topo-like pass.
        Assumes wires go strictly from outputs -> inputs (no bidirectional edges).
        If the user creates a cycle, nodes in that cycle just won't be in the queue;
        we still evaluate everything we can.
        """
        # 1) reset inputs and get graph
        self._reset_inputs()
        outgoing, indegree, incoming_map = self._build_graph()

        # 2) seed queue with nodes that have no incoming wires (sources)
        #    e.g., Switches, or unconnected gates (which will compute from default 0 inputs)
        queue = [c for c in self.components if indegree.get(c, 0) == 0]

        # 3) process in forward order
        visited = set()
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)

            # compute this node's output from its current inputs
            node.compute()

            # push its output along all outgoing wires
            for (to_comp, to_pin_idx) in outgoing.get(node, []):
                # set the specific input slot on the target from this node's output
                if to_comp.num_inputs > to_pin_idx:
                    to_comp.inputs[to_pin_idx] = 1 if getattr(node, "output", 0) else 0

                # decrement indegree and enqueue when all its inputs are fed
                indegree[to_comp] -= 1
                if indegree[to_comp] == 0:
                    queue.append(to_comp)

        # 4) final compute so sinks (e.g. Bulb) reflect their inputs
        for c in self.components:
            # For nodes not visited (e.g., cycles), do a compute anyway on whatever inputs they currently hold.
            if c not in visited:
                # populate inputs from incoming_map for any available edges
                if c.num_inputs:
                    for i in range(c.num_inputs):
                        src = incoming_map.get((c, i))
                        if src is not None:
                            c.inputs[i] = 1 if getattr(src, "output", 0) else 0
            c.compute()

    # -------- drawing --------
    def draw_palette(self):
        pygame.draw.rect(self.screen, PALETTE_BG, pygame.Rect(0, 0, PALETTE_W, HEIGHT))
        FONT.render_to(self.screen, (20, 20), "Palette", WHITE)
        for label, rect in self.palette:
            border = SELECT_C if (self.armed_type == label and label != "TRASH") else WHITE
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=8)
            # color TRASH background slightly
            if label == "TRASH":
                pygame.draw.rect(self.screen, (120, 40, 40), rect.inflate(-4, -4), 0, border_radius=6)
            FONT.render_to(self.screen, (rect.x + 10, rect.y + 10), label, WHITE)
        if self.armed_type:
            FONT.render_to(self.screen, (20, HEIGHT - 30), f"Placing: {self.armed_type}", YELLOW)

    def draw_grid(self):
        for x in range(CANVAS_X0, WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_LINE, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_LINE, (CANVAS_X0, y), (WIDTH, y), 1)

    def draw(self):
        self.screen.fill(BLUE)
        self.draw_palette()
        self.draw_grid()

        # update logic
        self.simulate()

        # wires first (so components/pins overlay)
        for w in self.wires:
            w.draw(self.screen)

        # components + pins
        hover = pygame.mouse.get_pos()
        hit_out = self.nearest_output_pin(hover)
        hit_in  = self.nearest_input_pin(hover)

        for comp in self.components:
            comp.draw(self.screen)
            for p in comp.get_output_pins():
                pygame.draw.circle(self.screen, GREEN, p, PIN_RADIUS)
            for p in comp.get_input_pins():
                pygame.draw.circle(self.screen, RED, p, PIN_RADIUS)

        # Hover highlight (pin cue)
        if hit_out:
            comp, idx = hit_out
            pygame.draw.circle(self.screen, (180, 255, 180), comp.get_output_pins()[idx], PIN_RADIUS + 2, 2)
        elif hit_in:
            comp, idx = hit_in
            pygame.draw.circle(self.screen, (255, 180, 180), comp.get_input_pins()[idx], PIN_RADIUS + 2, 2)

        # pending wire preview
        if self.pending_from:
            from_comp, out_idx = self.pending_from
            start = from_comp.get_output_pins()[out_idx]
            mouse = pygame.mouse.get_pos()
            pygame.draw.line(self.screen, YELLOW, start, mouse, 2)

        # back
        self.back_button.draw(self.screen)
        pygame.display.flip()
