import random
from collections import deque
import copy
import time

# Constants
GRID_WIDTH, GRID_HEIGHT = 6, 12
COLORS = ["red", "green", "blue", "yellow"]
EMPTY = None
PUYO_TEXT = {
    1: "⊚",    # Small Garbage Puyo
    6: "⚪",    # Large Garbage Puyo
    30: "🔴",   # Red nuisance puyo
    90: "⭐",   # Star Puyo
    180: "🌙",  # Moon Puyo
    360: "☄️",  # Comet Puyo
    720: "🪐",   # Saturn Puyo
    1000: "🃏",  # Club Puyo
    5000: "💎",  # Diamond Puyo
    20000: "❤️", # Heart Puyo
    100000: "♠️",# Spade Puyo
    500000: "👑", # Crown Puyo
    2000000: "🍄",# Mushroom Puyo
    10000000: "☀️",# Sun Puyo
    50000000: "🎩",# Top Hat Puyo
    200000000: "⚽",# Ball Puyo
    1000000000: "🎪",# Tent Puyo
}

class Puyo:
    def __init__(self, color):
        self.color = color
        self.state = 'normal'

class GameState:
    def __init__(self):
        self.grid = [[EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_puyo = self.generate_puyo()
        self.next_puyo = self.generate_puyo()
        self.score = 0
        self.running = True
        self.chain_count = 0

    def generate_puyo(self):
        return [[GRID_WIDTH // 2, 0, random.choice(COLORS)],
                [GRID_WIDTH // 2, 1, random.choice(COLORS)]]

    def drop_puyo(self):
        if self.current_puyo:
            if not self.is_valid_move(self.current_puyo, dy=1):
                self.lock_puyo()
                self.current_puyo = None
                self.chain_count = 0
                self.resolve()
            else:
                for puyo in self.current_puyo:
                    puyo[1] += 1

    def lock_puyo(self):
        for x, y, color in self.current_puyo:
            self.grid[y][x] = Puyo(color)

    def resolve(self):
        self.find_matches()
        if not self.current_puyo:
            self.current_puyo = self.next_puyo
            self.next_puyo = self.generate_puyo()
            if not self.is_valid_move(self.current_puyo):
                self.running = False  # Game over

    def find_matches(self):
        to_clear = []
        visited = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                puyo = self.grid[y][x]
                if puyo and not visited[y][x] and puyo.state == 'normal':
                    connected = self.get_connected_puyos(x, y, visited)
                    if len(connected) >= 4:
                        to_clear.extend(connected)
        for x, y in to_clear:
            self.grid[y][x] = EMPTY
        self.update_score(len(to_clear))

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
                    if neighbor and not visited[ny][nx] and neighbor.color == color:
                        queue.append((nx, ny))
        return connected

    def update_score(self, cleared_puyos):
        self.score += cleared_puyos 
        print(f"Score updated! Cleared {cleared_puyos} puyos. Total score: {self.score}")

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

class PuyoGame:
    def __init__(self):
        self.state = GameState()

    def draw(self):
        print("\nCurrent Game State:")
        for row in self.state.grid:
            row_display = []
            for puyo in row:
                if puyo:
                    row_display.append(PUYO_TEXT[1])  # Display small puyo for simplicity
                else:
                    row_display.append(" ")
            print(" | ".join(row_display))
        print(f"Score: {self.state.score}")

    def update(self):
        if self.state.current_puyo:
            self.state.drop_puyo()

    def handle_input(self):
        action = input("Enter command (left, right, drop, rotate, quit): ").strip().lower()
        if action == "quit":
            self.state.running = False
        # Add more input handling for left, right, drop, rotate as needed

def main():
    game = PuyoGame()
    while game.state.running:
        game.draw()
        game.handle_input()
        game.update()
        time.sleep(0.5)  # Simulate game loop delay

    print("Game Over!")

if __name__ == "__main__":
    main()