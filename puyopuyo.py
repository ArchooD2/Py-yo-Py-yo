import pygame
import random
from collections import deque
import copy
from time import sleep as wait
# Initialize pygame
pygame.init()
crazy = False  # Set to True to enable crazy mode
# Constants
GRID_WIDTH, GRID_HEIGHT = 6, 12
TILE_SIZE = 40
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = (GRID_HEIGHT + 2) * TILE_SIZE
FPS = 60
COLORS = ["red", "green", "blue", "yellow"]
EMPTY = None
# Full mapping of nuisance Puyo values to their emoji representations
PUYO_EMOJIS = {
    1: "Nuisance_small_puyo4.png",
    6: "Nuisance_large_puyo4.png",
    30: "Nuisance_rock_puyo4.png",
    90: "Nuisance_star_puyo4.png",
    180: "Nuisance_moon_puyo4.png",
    360: "Nuisance_comet_puyo4.png",
    720: "Nuisance_saturn_puyo4.png",
    1000: "Nuisance_club_puyo4.png",
    5000: "Nuisance_diamond_puyo4.png",
    20000: "Nuisance_heart_puyo4.png",
    100000: "Nuisance_spade_puyo4.png",
    500000: "Nuisance_crown_puyo4.png",
    2000000: "Nuisance_mushroom_puyo4.png",
    10000000: "Nuisance_sun_puyo4.png",
    50000000: "Nuisance_tophat_puyo4.png",
    200000000: "Nuisance_ball_puyo4.png",
    1000000000: "Nuisance_tent_puyo4.png",
    5000000000: "Nuisance_GD-Rom_puyo4.png",
    10000000000: "Nuisance_blueswirl_puyo4.png",
    50000000000: "Nuisance_greenswirl_puyo4.png",
    100000000000: "Nuisance_yellowswirl_puyo4.png",
    500000000000: "Nuisance_purpleswirl_puyo4.png",
    1000000000000: "Nuisance_redswirl_puyo4.png",
}
PUYO_TEXT = {
    1: "⊚",              # Small Garbage Puyo
    6: "⚪",       # Large Garbage Puyo (6 small ones)
    30: "♪",            # Red nuisance puyo (rock)
    90: "⭐",            # Star Puyo
    180: "🌙",           # Moon Puyo
    360: "☄️",          # Comet Puyo
    720: "🪐",           # Saturn Puyo
    1000: "🃏",           # Club Puyo
    5000: "💎",          # Diamond Puyo
    20000: "❤️",         # Heart Puyo
    100000: "♠️",        # Spade Puyo
    500000: "👑",        # Crown Puyo
    2000000: "🍄",       # Mushroom Puyo
    10000000: "☀️",     # Sun Puyo
    50000000: "🎩",      # Top Hat Puyo
    200000000: "⚽",     # Ball Puyo
    1000000000: "🎪",    # Tent Puyo
    5000000000: "💿",    # GD-ROM Puyo
    10000000000: "🔵",   # Blue Swirl Puyo
    50000000000: "🟢",   # Green Swirl Puyo
    100000000000: "🟡",  # Yellow Swirl Puyo
    500000000000: "🟣",  # Purple Swirl Puyo
    1000000000000: "🔴", # Red Swirl Puyo
}
# Load nuisance images
nuisance_images = {value: pygame.image.load(f"nuisance_images/{filename}") for value, filename in PUYO_EMOJIS.items()}

def get_puyo_image(nuisance_count):
    """Get the appropriate image for a given nuisance count."""
    images = []
    for value, image in sorted(nuisance_images.items(), reverse=True):
        while nuisance_count >= value:
            images.append(image)
            nuisance_count -= value
    return images

def get_puyo_text(nuisance_count):
    """Get the appropriate text representation for a given nuisance count."""
    text = ""
    for value in sorted(PUYO_TEXT.keys(), reverse=True):
        while nuisance_count >= value:
            text += PUYO_TEXT[value]
            nuisance_count -= value
    return text

# Animation Constants
POP_TIME = 0.7  # Duration of the pop animation in seconds
last_nuisance = []  # To store the last nuisance text and images to display
# Scoring Constants
CHAIN_BONUS = [0, 8, 16, 32, 64, 96, 128, 160, 192, 224, 256]
COLOR_BONUS = [0, 3, 6, 12, 24]
GROUP_BONUS = [0, 2, 3, 4, 5, 6, 7, 10]

# Colors for pygame display
COLOR_MAP = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    EMPTY: (0, 0, 0)
}

class Puyo:
    def __init__(self, color, state='normal', animation_timer=0):
        global crazy
        self.color = color
        self.state = state  # 'normal', 'popping'
        self.animation_timer = animation_timer  # Timer for animations

class GameState:
    def __init__(self, grid=None, current_puyo=None, next_puyo=None, score=0, fall_timer=0, fall_speed=30, running=True):
        self.grid = grid if grid else [[EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_puyo = current_puyo if current_puyo else self.generate_puyo()
        self.next_puyo = next_puyo if next_puyo else self.generate_puyo()
        self.score = score
        self.fall_timer = fall_timer
        self.fall_speed = fall_speed
        self.running = running
        self.clearing = False  # Flag to indicate if clearing animation is happening
        self.chain_count = 0
        self.delta_time = 0

    def generate_puyo(self):
        return [[GRID_WIDTH // 2, 0, random.choice(COLORS)],
                [GRID_WIDTH // 2, 1, random.choice(COLORS)]]

    def clone(self):
        return GameState(
            grid=[[copy.deepcopy(cell) for cell in row] for row in self.grid],
            current_puyo=copy.deepcopy(self.current_puyo),
            next_puyo=copy.deepcopy(self.next_puyo),
            score=self.score,
            fall_timer=self.fall_timer,
            fall_speed=self.fall_speed,
            running=self.running
        )

    def process_input(self, action):
        if self.current_puyo and not self.clearing:  # Prevent input during clearing
            if action == 'left':
                if self.is_valid_move(self.current_puyo, dx=-1):
                    for puyo in self.current_puyo:
                        puyo[0] -= 1
            elif action == 'right':
                if self.is_valid_move(self.current_puyo, dx=1):
                    for puyo in self.current_puyo:
                        puyo[0] += 1
            elif action == 'rotate':
                self.rotate_puyo()
            elif action == 'drop':
                self.drop_puyo()
            elif action == 'hard_drop':
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
            self.current_puyo = None
            self.chain_count = 0
            self.resolve()
    def rotate_puyo(self):
        if self.current_puyo:
            pivot = self.current_puyo[0]
            satellite = self.current_puyo[1]
            dx = satellite[0] - pivot[0]
            dy = satellite[1] - pivot[1]
            new_dx = -dy
            new_dy = dx
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
                puyo.state = 'popping'
                puyo.animation_timer = 0
        else:
            # No more matches, spawn new puyo
            self.current_puyo = self.next_puyo
            self.next_puyo = self.generate_puyo()
            if not self.is_valid_move(self.current_puyo):
                self.running = False  # Game over

    def find_matches(self):
        self.to_clear = []
        self.colors_cleared = set()
        self.groups_cleared = []
        visited = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                puyo = self.grid[y][x]
                if puyo and not visited[y][x] and puyo.state == 'normal':
                    connected = self.get_connected_puyos(x, y, visited)
                    if len(connected) >= 4:
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
                if (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT):
                    neighbor = self.grid[ny][nx]
                    if neighbor and not visited[ny][nx] and neighbor.color == color and neighbor.state == 'normal':
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
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT - 2, -1, -1):
                if self.grid[y][x] and self.grid[y + 1][x] == EMPTY:
                    self.grid[y + 1][x] = self.grid[y][x]
                    self.grid[y][x] = EMPTY
                    moved = True
        return moved

    def update_score(self, cleared_puyos, chain_count):
        chain_bonus = CHAIN_BONUS[min(chain_count - 1, len(CHAIN_BONUS) - 1)]
        if crazy:
            chain_bonus = 4*(2**chain_count)
        color_bonus = COLOR_BONUS[min(len(self.colors_cleared) - 1, len(COLOR_BONUS) - 1)] if len(self.colors_cleared) > 0 else 0
        group_bonus = sum([GROUP_BONUS[min(size - 4, len(GROUP_BONUS) - 1)] for size in self.groups_cleared])
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
        last_nuisance = image_representation
        # Print statement reflecting chain score, cleared puyos, and nuisance details
        if text_representation:
            print(f"Chain {chain_count}: {cleared_puyos} puyos cleared (+{score_increment}) -> Nuisance Puyo: {text_representation} ({NC}) (+{NL:.2f} leftover)")
        else:
            print(f"Chain {chain_count}: {cleared_puyos} puyos cleared (+{score_increment}) -> Nuisance Puyo: None (0) (+{NL:.2f} leftover)")

    def is_valid_move(self, puyo_pair, dx=0, dy=0):
        for x, y, color in puyo_pair:
            nx, ny = x + dx, y + dy
            if not self.is_valid_position(nx, ny):
                return False
        return True

    def is_valid_position(self, x, y):
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return False
        if self.grid[y][x]:
            return False
        return True

    def is_running(self):
        return self.running
    

class PuyoGame:
    def __init__(self):
        global lastgrid
        self.state = GameState()
        # Initialize pygame elements
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Puyo Puyo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.nuisance_images = []  # To store the nuisance images to display

    def draw(self):
        self.screen.fill((0, 0, 0))
        # Draw the score
        score_text = self.font.render(f"Score: {self.state.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        self.update_nuisance_images(last_nuisance)  # Update the nuisance images display
        # Draw the nuisance images above the playable area
        x_offset = 10
        for image in self.nuisance_images:
            self.screen.blit(image, (x_offset, 40))
            x_offset += image.get_width() + 5

        # Draw the grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                puyo = self.state.grid[y][x]
                if puyo:
                    # Handle popping animation
                    if puyo.state == 'popping':
                        progress = puyo.animation_timer / POP_TIME
                        scale = max(1.0 - progress, 0)
                        alpha = max(255 * (1.0 - progress), 0)
                        color = COLOR_MAP[puyo.color]
                        color_with_alpha = (color[0], color[1], color[2], int(alpha))
                        puyo_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                        rect = pygame.Rect(
                            TILE_SIZE * (1 - scale) / 2,
                            TILE_SIZE * (1 - scale) / 2,
                            TILE_SIZE * scale,
                            TILE_SIZE * scale
                        )
                        pygame.draw.rect(puyo_surface, color_with_alpha, rect)
                        puyo_rect = puyo_surface.get_rect(
                            topleft=(x * TILE_SIZE, (y + 2) * TILE_SIZE)
                        )
                        self.screen.blit(puyo_surface, puyo_rect)
                    else:
                        pygame.draw.rect(self.screen, COLOR_MAP[puyo.color],
                                         (x * TILE_SIZE, (y + 2) * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                        pygame.draw.rect(self.screen, (255, 255, 255),
                                         (x * TILE_SIZE, (y + 2) * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

        # Draw the current Puyo pair if not in clearing state
        if self.state.current_puyo:
            for x, y, color in self.state.current_puyo:
                pygame.draw.rect(self.screen, COLOR_MAP[color],
                                 (x * TILE_SIZE, (y + 2) * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(self.screen, (255, 255, 255),
                                 (x * TILE_SIZE, (y + 2) * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
        pygame.display.flip()

    def update(self):
        delta_time = self.clock.tick(FPS) / 1000.0  # Convert to seconds
        if not self.state.clearing:
            self.state.fall_timer += 1
            if self.state.fall_timer >= self.state.fall_speed:
                self.state.drop_puyo()
                self.state.fall_timer = 0
        else:
            self.state.update_clearing(delta_time)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state.running = False
    def is_running(self):
        return self.state.is_running()

    def process_input(self, action):
        self.state.process_input(action)

    def update_nuisance_images(self, nuisance_images):
        """Update the nuisance images display."""
        self.nuisance_images = nuisance_images


def main():
    game = PuyoGame()

    while game.is_running():
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.process_input('left')
                elif event.key == pygame.K_RIGHT:
                    game.process_input('right')
                elif event.key == pygame.K_DOWN:
                    game.process_input('drop')
                elif event.key == pygame.K_UP:
                    game.process_input('rotate')
                elif event.key == pygame.K_SPACE:
                    game.state.hard_drop()
            elif event.type == pygame.QUIT:
                game.state.running = False
        game.handle_events()
        game.update()
        game.draw()

    pygame.quit()

if __name__ == "__main__":
    main()
    print("Game Over!")
