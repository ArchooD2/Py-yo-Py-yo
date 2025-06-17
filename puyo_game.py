import pygame
from time import time
from constants import *
from assets import nuisance_images
from game_state import GameState
from utils import get_puyo_image, get_puyo_text

class PuyoGame:
    def __init__(self, state: GameState, tile_size: int, screen_width: int, screen_height: int):
        """
        :param state:         the GameState instance (grid, score, etc.)
        :param tile_size:     size in pixels of one puyo tile
        :param screen_width:  total window width in pixels
        :param screen_height: total window height in pixels
        """
        global lastgrid, SCREEN_WIDTH, SCREEN_HEIGHT

        # Use the externally provided state
        self.state = state
        self.grid_width = state.grid_width
        self.grid_height = state.grid_height
        self.required_group_number = state.required_group_number

        # Tile size and screen dimensions
        self.TILE_SIZE = tile_size
        SCREEN_WIDTH, SCREEN_HEIGHT = screen_width, screen_height
        lastgrid = state.clone().grid

        # Initialize pygame elements
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Puyo Puyo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        # For nuisance display and fast-drop
        self.nuisance_images = []
        self.is_down_pressed = False
        self.game_over = False

    def draw(self):
        self.screen.fill((0, 0, 0))

        # Score
        score_text = self.font.render(f"Score: {self.state.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        # Time
        elapsed = "gameover" if not self.state.running else int(time() - self.state.start_time)
        ttxt = f"Time: {elapsed}{'s' if elapsed != 'gameover' else ''}"
        time_text = self.font.render(ttxt, True, (255, 255, 255))
        self.screen.blit(time_text, (10, 40))

        # Chain
        chain_text = self.font.render(f"Chain: {self.state.chain_count}", True, (255, 255, 255))
        self.screen.blit(chain_text, (10, 70))

        # Next puyo
        for x, y, color in self.state.next_puyo:
            nx = SCREEN_WIDTH - 180 + x * self.TILE_SIZE
            ny = 40 + y * self.TILE_SIZE
            pygame.draw.rect(self.screen, COLOR_MAP[color], (nx, ny, self.TILE_SIZE, self.TILE_SIZE))
            pygame.draw.rect(self.screen, (255, 255, 255), (nx, ny, self.TILE_SIZE, self.TILE_SIZE), 1)

        # Next-next puyo
        for x, y, color in self.state.next_next_puyo:
            nx = SCREEN_WIDTH - 180 + x * self.TILE_SIZE
            ny = 150 + y * self.TILE_SIZE
            pygame.draw.rect(self.screen, COLOR_MAP[color], (nx, ny, self.TILE_SIZE, self.TILE_SIZE))
            pygame.draw.rect(self.screen, (255, 255, 255), (nx, ny, self.TILE_SIZE, self.TILE_SIZE), 1)

        # Nuisance images
        self.update_nuisance_images(self.state.last_nuisance_images)
        yoff = 200
        for img in self.nuisance_images:
            self.screen.blit(img, (SCREEN_WIDTH - 180, yoff))
            yoff += img.get_height() + 5

        # Grid & placed puyos
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = (x * self.TILE_SIZE, (y + 4) * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE)
                pygame.draw.rect(self.screen, (128, 128, 128), rect, 1)
                cell = self.state.grid[y][x]
                if cell:
                    if cell.state == "popping":
                        # popping animation
                        progress = cell.animation_timer / POP_TIME
                        scale = max(1.0 - progress, 0)
                        alpha = max(255 * (1.0 - progress), 0)
                        surf = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
                        color = (*COLOR_MAP[cell.color], int(alpha))
                        inset = self.TILE_SIZE * (1 - scale) / 2
                        pygame.draw.rect(surf, color,
                                         (inset, inset, self.TILE_SIZE*scale, self.TILE_SIZE*scale))
                        self.screen.blit(surf, (x*self.TILE_SIZE, (y+4)*self.TILE_SIZE))
                    else:
                        pygame.draw.rect(self.screen, COLOR_MAP[cell.color],
                                         rect)
                        pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)

        # Current falling puyo
        if self.state.current_puyo:
            for x, y, color in self.state.current_puyo:
                rect = (x*self.TILE_SIZE, (y+4)*self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE)
                pygame.draw.rect(self.screen, COLOR_MAP[color], rect)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)

        # Game over message
        if not self.state.running:
            go = self.font.render("Game Over! Close window to exit.", True, (255, 0, 0))
            self.screen.blit(go, ((SCREEN_WIDTH-go.get_width())//2, SCREEN_HEIGHT//2))

        pygame.display.flip()

    def update(self):
        delta = self.clock.tick(FPS) / 1000.0
        if not self.state.clearing:
            # fast drop if holding down
            self.state.fall_timer += 5 if self.is_down_pressed else 1
            if self.state.fall_timer >= self.state.fall_speed:
                self.state.drop_puyo()
                self.state.fall_timer = 0
        else:
            self.state.update_clearing(delta)

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.state.running = False
                self.game_over = True
            elif ev.type == pygame.KEYDOWN and self.state.running:
                if ev.key == pygame.K_LEFT:
                    self.state.process_input("left")
                elif ev.key == pygame.K_RIGHT:
                    self.state.process_input("right")
                elif ev.key == pygame.K_DOWN:
                    self.is_down_pressed = True
                    self.state.process_input("drop")
                elif ev.key in (pygame.K_UP, pygame.K_z):
                    self.state.process_input("rotate_cw")
                elif ev.key == pygame.K_x:
                    self.state.process_input("rotate_ccw")
            elif ev.type == pygame.KEYUP:
                if ev.key == pygame.K_DOWN:
                    self.is_down_pressed = False

    def update_nuisance_images(self, nuisance_list):
        self.nuisance_images = nuisance_list[:4]

    def is_running(self):
        return not self.game_over