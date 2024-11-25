# Import necessary classes and functions from the Puyo game script
from puyopuyo import GameState
import os
import time
GRID_WIDTH, GRID_HEIGHT = 6, 12

class PuyoAI:
    def __init__(self):
        self.actions = ['left', 'right', 'rotate', 'hard_drop']

    def simulate_move(self, game_state, action):
        """Clone the game state and simulate the given move."""
        cloned_state = game_state.clone()
        cloned_state.process_input(action)
        return cloned_state

    def evaluate_state(self, game_state):
        """Heuristic function to evaluate a game state."""
        chain_bonus = game_state.chain_count
        open_spaces = sum(row.count(None) for row in game_state.grid)
        color_variety = len({puyo.color for row in game_state.grid for puyo in row if puyo})
        return chain_bonus * 1000 + open_spaces + color_variety * 10

    def find_best_move(self, game_state):
        """Find the best action based on simulations."""
        best_score = -float('inf')
        best_action = None
        for action in self.actions:
            simulated_state = self.simulate_move(game_state, action)
            score = self.evaluate_state(simulated_state)
            if score > best_score:
                best_score = score
                best_action = action
        return best_action


def print_grid(grid, current_puyo, next_puyo, score):
    """Display the grid with better formatting and styling."""
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen
    print("\033[1m\033[94m" + "Puyo Puyo AI Game" + "\033[0m")
    print(f"Score: \033[92m{score}\033[0m\n")

    # Print grid border
    print("  " + "+----" * len(grid[0]) + "+")

    for y, row in enumerate(grid):
        print("  |", end="")
        for cell in row:
            if cell is None:
                print("    ", end="")  # Empty space
            else:
                color = cell.color[0].upper()  # First letter of color
                color_code = {
                    'R': "\033[91m",  # Red
                    'G': "\033[92m",  # Green
                    'B': "\033[94m",  # Blue
                    'Y': "\033[93m"   # Yellow
                }.get(color, "\033[0m")  # Default to no color
                print(f" {color_code}{color}\033[0m ", end="")
        print("|")

    print("  " + "+----" * len(grid[0]) + "+\n")

    # Display current and next Puyo
    if current_puyo:
        print("\033[93mCurrent Puyo:\033[0m")
        for x, y, color in current_puyo:
            print(f"    {color.capitalize()} at ({x}, {y})")

    if next_puyo:
        print("\033[94mNext Puyo:\033[0m")
        for x, y, color in next_puyo:
            print(f"    {color.capitalize()}")

    print("\n")


def main():
    game_state = GameState()
    ai = PuyoAI()
    fall_timer = 0
    fall_speed = 5  # Adjust fall speed as needed

    while game_state.is_running():
        # Use AI to decide the best move
        best_action = ai.find_best_move(game_state)
        print(f"Best Action: {best_action}")
        if best_action:
            game_state.process_input(best_action)

        # Update fall timer
        fall_timer += 1
        if fall_timer >= fall_speed:
            game_state.drop_puyo()
            fall_timer = 0

        # If the falling puyo can't move down anymore, hard drop it instantly.
        try:
            if game_state.current_puyo:
                if not game_state.is_valid_move(game_state.current_puyo, dy=1):
                    game_state.hard_drop()
                    game_state.resolve()
        except Exception as e:
            print({e})
            break
        # Display the game state
        print_grid(game_state.grid, game_state.current_puyo, game_state.next_puyo, game_state.score)
        time.sleep(0.1)  # Adjust delay as needed

    print("\033[91mGame Over! Final Score:\033[0m", game_state.score)



if __name__ == "__main__":
    main()
