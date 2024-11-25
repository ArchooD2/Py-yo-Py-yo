import pygame
import random

# Initialize pygame
pygame.init()

# Constants
GRID_WIDTH, GRID_HEIGHT = 5, 6
TILE_SIZE = 40
UI_SPACE = 100  # Space above the grid for scores/UI
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = (GRID_HEIGHT + 1) * TILE_SIZE + UI_SPACE
FPS = 60
COLORS = ["red", "green", "blue", "yellow", "pink"]
EMPTY = None

COLOR_MAP = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "pink": (255, 105, 180),
    EMPTY: (0, 0, 0)
}

class Puyo:
    def __init__(self, color):
        self.color = color


class GameState:
    def __init__(self):
        self.grid = [[EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_puyo = self.generate_puyo()
        self.running = True

    def generate_puyo(self):
        """Generate a new pair of Puyos in the placement row."""
        return [
            [GRID_WIDTH // 2, -1, random.choice(COLORS)],
            [GRID_WIDTH // 2 + 1, -1, random.choice(COLORS)]
        ]

    def place_puyo(self, column):
        """Place the current Puyo pair in the specified column and apply gravity."""
        if not self.is_valid_column(column):
            return  # Do nothing if the column is invalid

        # Adjust current Puyo pair to align with the selected column
        for i, (x, y, color) in enumerate(self.current_puyo):
            self.current_puyo[i][0] = column + i

        # Place Puyo pair into the grid
        for x, y, color in self.current_puyo:
            if y >= 0:  # Only place within the grid
                self.grid[y][x] = Puyo(color)

        self.current_puyo = self.generate_puyo()  # Generate the next Puyo pair
        self.apply_gravity()  # Apply gravity to the grid

    def rotate_puyo(self):
        """Rotate the Puyo pair clockwise."""
        pivot = self.current_puyo[0]
        satellite = self.current_puyo[1]
        dx = satellite[0] - pivot[0]
        dy = satellite[1] - pivot[1]
        new_dx = -dy
        new_dy = dx
        new_satellite = [pivot[0] + new_dx, pivot[1] + new_dy, satellite[2]]
        # Ensure the rotation stays within bounds
        if 0 <= new_satellite[0] < GRID_WIDTH:
            self.current_puyo[1] = new_satellite

    def apply_gravity(self):
        """Apply gravity to the grid."""
        moved = True
        while moved:
            moved = False
            for y in range(GRID_HEIGHT - 1, 0, -1):
                for x in range(GRID_WIDTH):
                    if self.grid[y][x] == EMPTY and self.grid[y - 1][x] is not None:
                        self.grid[y][x] = self.grid[y - 1][x]
                        self.grid[y - 1][x] = EMPTY
                        moved = True

    def is_valid_column(self, column):
        """Check if the column is valid for placement."""
        return 0 <= column < GRID_WIDTH and self.grid[0][column] == EMPTY

    def is_running(self):
        return self.running


class PuyoGame:
    def __init__(self):
        self.state = GameState()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Simpler Puyo Puyo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

    def draw(self):
        self.screen.fill((0, 0, 0))
        # Draw the UI area
        score_text = self.font.render("Score: 0", True, (255, 255, 255))  # Placeholder score
        self.screen.blit(score_text, (10, 10))

        # Draw the grid
        for y in range(-1, GRID_HEIGHT):  # Include the placement row
            for x in range(GRID_WIDTH):
                puyo = self.state.grid[y][x] if y >= 0 else None
                if y == -1:  # Draw placement row background
                    pygame.draw.rect(self.screen, (50, 50, 50),
                                     (x * TILE_SIZE, UI_SPACE + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                if puyo:
                    pygame.draw.rect(self.screen, COLOR_MAP[puyo.color],
                                     (x * TILE_SIZE, UI_SPACE + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(self.screen, (255, 255, 255),
                                 (x * TILE_SIZE, UI_SPACE + y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

        # Draw the current Puyo pair
        for x, y, color in self.state.current_puyo:
            pygame.draw.rect(self.screen, COLOR_MAP[color],
                             (x * TILE_SIZE, UI_SPACE + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(self.screen, (255, 255, 255),
                             (x * TILE_SIZE, UI_SPACE + y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                column = pygame.mouse.get_pos()[0] // TILE_SIZE
                if event.button == 1:  # Left click to place
                    self.state.place_puyo(column)
                elif event.button == 3:  # Right click to rotate
                    self.state.rotate_puyo()

    def update(self):
        self.clock.tick(FPS)

    def is_running(self):
        return self.state.is_running()


def main():
    game = PuyoGame()

    while game.is_running():
        game.handle_events()
        game.update()
        game.draw()

    pygame.quit()


if __name__ == "__main__":
    main()
