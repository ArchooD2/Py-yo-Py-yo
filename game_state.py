import random
import copy
from time import time
from collections import deque
from constants import *
from utils import get_puyo_image, get_puyo_text
from puyo import Puyo

class GameState:
    def __init__(
        self,
        grid=None,
        grid_width=DEFAULT_GRID_WIDTH,
        grid_height=DEFAULT_GRID_HEIGHT,
        current_puyo=None,
        next_puyo=None,
        next_next_puyo=None,
        score=0,
        fall_timer=0,
        fall_speed=30,
        running=True,
        required_group_number=4,
        crazy=False,
    ):
        self.required_group_number = required_group_number
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid = (
            grid
            if grid
            else [[EMPTY for _ in range(grid_width)] for _ in range(grid_height)]
        )
        self.current_puyo = current_puyo if current_puyo else self.generate_puyo()
        self.next_puyo = next_puyo if next_puyo else self.generate_puyo()
        self.next_next_puyo = next_next_puyo if next_next_puyo else self.generate_puyo()
        self.score = score
        self.fall_timer = fall_timer
        self.fall_speed = fall_speed
        self.running = running
        self.clearing = False  # Flag to indicate if clearing animation is happening
        self.chain_count = 0
        self.delta_time = 0
        self.crazy = crazy
        self.start_time = time()  # Track the time the game starts
        self.last_nuisance_images: list[pygame.Surface] = []
        self.last_nuisance_text: str = ""

    def generate_puyo(self):
        return [
            [(self.grid_width - 1) // 2, 0, random.choice(COLORS)],
            [(self.grid_width - 1) // 2, 1, random.choice(COLORS)],
        ]

    def clone(self):
        return GameState(
            grid=[[copy.deepcopy(cell) for cell in row] for row in self.grid],
            current_puyo=copy.deepcopy(self.current_puyo),
            next_puyo=copy.deepcopy(self.next_puyo),
            next_next_puyo=copy.deepcopy(self.next_next_puyo),
            score=self.score,
            fall_timer=self.fall_timer,
            fall_speed=self.fall_speed,
            running=self.running,
        )

    def process_input(self, action):
        if self.current_puyo and not self.clearing:  # Prevent input during clearing
            if action == "left":
                if self.is_valid_move(self.current_puyo, dx=-1):
                    for puyo in self.current_puyo:
                        puyo[0] -= 1
            elif action == "right":
                if self.is_valid_move(self.current_puyo, dx=1):
                    for puyo in self.current_puyo:
                        puyo[0] += 1
            elif action == "rotate_cw":  # Clockwise rotation
                self.rotate_puyo(clockwise=True)
            elif action == "rotate_ccw":  # Counter-clockwise rotation
                self.rotate_puyo(clockwise=False)
            elif action == "drop":
                self.drop_puyo()
            elif action == "hard_drop":
                self.hard_drop()

    def drop_puyo(self):
        if self.current_puyo:
            if not self.is_valid_move(self.current_puyo, dy=1):
                self.lock_puyo()
                self.current_puyo = None  # Remove current puyo from play
                self.chain_count = 0  # Reset chain count
                self.resolve()
            else:
                for puyo in self.current_puyo:
                    puyo[1] += 1

    def hard_drop(self):
        if self.current_puyo:
            while self.is_valid_move(self.current_puyo, dy=1):
                for puyo in self.current_puyo:
                    puyo[1] += 1
            self.lock_puyo()
            self.fall_timer = 0
            self.current_puyo = None
            self.chain_count = 0
            self.resolve()

    def rotate_puyo(self, clockwise=True):
        if self.current_puyo:
            pivot = self.current_puyo[0]
            satellite = self.current_puyo[1]
            dx = satellite[0] - pivot[0]
            dy = satellite[1] - pivot[1]
            if clockwise:
                new_dx = -dy
                new_dy = dx
            else:  # Counter-clockwise
                new_dx = dy
                new_dy = -dx
            new_satellite = [pivot[0] + new_dx, pivot[1] + new_dy, satellite[2]]
            if self.is_valid_position(new_satellite[0], new_satellite[1]):
                self.current_puyo[1] = new_satellite

    def lock_puyo(self):
        for x, y, color in self.current_puyo:
            self.grid[y][x] = Puyo(color)

    def resolve(self):
        while self.apply_gravity():
            pass
        self.find_matches()
        if self.to_clear:
            self.clearing = True
            self.chain_count += 1
            for x, y in self.to_clear:
                puyo = self.grid[y][x]
                puyo.state = "popping"
                puyo.animation_timer = 0
        else:
            # No more matches, spawn new puyo
            self.current_puyo = self.next_puyo
            self.next_puyo = self.next_next_puyo
            self.next_next_puyo = self.generate_puyo()
            if not self.is_valid_move(self.current_puyo):
                self.running = False  # Game over

    def find_matches(self):
        self.to_clear = []
        self.colors_cleared = set()
        self.groups_cleared = []
        visited = [
            [False for _ in range(self.grid_width)] for _ in range(self.grid_height)
        ]

        for y in range(self.grid_height):  # Use self.grid_height
            for x in range(self.grid_width):  # Use self.grid_width
                puyo = self.grid[y][x]
                if puyo and not visited[y][x] and puyo.state == "normal":
                    connected = self.get_connected_puyos(x, y, visited)
                    if len(connected) >= self.required_group_number:
                        self.to_clear.extend(connected)
                        self.colors_cleared.add(puyo.color)
                        self.groups_cleared.append(len(connected))

    def get_connected_puyos(self, x, y, visited):
        color = self.grid[y][x].color
        queue = deque()
        queue.append((x, y))
        connected = []
        while queue:
            cx, cy = queue.popleft()
            if visited[cy][cx]:
                continue
            visited[cy][cx] = True
            connected.append((cx, cy))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if (
                    0 <= nx < self.grid_width and 0 <= ny < self.grid_height
                ):  # Use self.grid_width and self.grid_height
                    neighbor = self.grid[ny][nx]
                    if (
                        neighbor
                        and not visited[ny][nx]
                        and neighbor.color == color
                        and neighbor.state == "normal"
                    ):
                        queue.append((nx, ny))
        return connected

    def update_clearing(self, delta_time):
        animation_complete = True
        for x, y in self.to_clear:
            puyo = self.grid[y][x]
            puyo.animation_timer += delta_time
            if puyo.animation_timer < POP_TIME:
                animation_complete = False
        if animation_complete:
            # Remove the puyos after animation
            cleared_puyos = len(self.to_clear)
            for x, y in self.to_clear:
                self.grid[y][x] = EMPTY
            self.update_score(cleared_puyos, self.chain_count)
            self.clearing = False
            # After clearing, apply gravity and check for more matches
            self.resolve()

    def apply_gravity(self):
        moved = False
        for y in range(self.grid_height - 2, -1, -1):  # Start from second to last row
            for x in range(self.grid_width):
                if self.grid[y][x]:  # Check if there's a puyo at (x, y)
                    # Ensure we are not accessing out-of-bounds by checking y + 1
                    if y + 1 < self.grid_height and self.grid[y + 1][x] == EMPTY:
                        # Move the puyo down
                        self.grid[y + 1][x] = self.grid[y][x]
                        self.grid[y][x] = EMPTY
                        moved = True
        return moved

    def update_score(self, cleared_puyos, chain_count):
        chain_bonus = CHAIN_BONUS[min(chain_count - 1, len(CHAIN_BONUS) - 1)]
        if self.crazy:
            chain_bonus = 4 * (2**chain_count)
        color_bonus = (
            COLOR_BONUS[min(len(self.colors_cleared) - 1, len(COLOR_BONUS) - 1)]
            if len(self.colors_cleared) > 0
            else 0
        )
        group_bonus = sum(
            [
                GROUP_BONUS[min(size - 4, len(GROUP_BONUS) - 1)]
                for size in self.groups_cleared
            ]
        )
        total_bonus = chain_bonus + color_bonus + group_bonus
        if total_bonus == 0:
            total_bonus = 1
        score_increment = cleared_puyos * 10 * total_bonus
        self.score += score_increment
        # Nuisance point calculation
        current_chain_score = self.score  # Or pass in SC if calculated separately
        TP = 70  # Target points for one nuisance puyo
        NP = current_chain_score / TP
        NC = int(NP)  # Rounded down
        NL = NP - NC  # Leftover

        # Get image and text representation for nuisance puyos
        text_representation = get_puyo_text(NC)
        image_representation = get_puyo_image(NC)
        global last_nuisance
        self.last_nuisance_text = text_representation
        self.last_nuisance_images = image_representation
        # Print statement reflecting chain score, cleared puyos, and nuisance details
        if text_representation:
            print(
                f"Chain {chain_count}: {cleared_puyos} puyos cleared (+{score_increment}) -> Nuisance Puyo: {text_representation} ({NC}) (+{NL:.2f} leftover)"
            )
        else:
            print(
                f"Chain {chain_count}: {cleared_puyos} puyos cleared (+{score_increment}) -> Nuisance Puyo: None (0) (+{NL:.2f} leftover)"
            )

    def is_valid_move(self, puyo_pair, dx=0, dy=0):
        for x, y, color in puyo_pair:
            nx, ny = x + dx, y + dy
            if not self.is_valid_position(nx, ny):
                return False
        return True

    def is_valid_position(self, x, y):
        # Check if x and y are within grid boundaries
        if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
            return False
        return not self.grid[y][x]

    def is_running(self):
        return self.running