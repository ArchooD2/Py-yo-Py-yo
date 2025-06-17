import pygame
from constants import *
from utils import calculate_tile_size
from game_state import GameState
from puyo_game import PuyoGame

pygame.init()

def main():
    if input("Customize? (y/n):").lower()=='y':
        w = int(input(f"Width ({DEFAULT_GRID_WIDTH}):") or DEFAULT_GRID_WIDTH)
        h = int(input(f"Height ({DEFAULT_GRID_HEIGHT}):") or DEFAULT_GRID_HEIGHT)
    else:
        w, h = DEFAULT_GRID_WIDTH, DEFAULT_GRID_HEIGHT
    size = calculate_tile_size(w, h, BASE_TILE_SIZE, MAX_SCREEN_WIDTH, MAX_SCREEN_HEIGHT)
    sw, sh = size*(w+5), size*(h+6)
    state = GameState(None, w, h)
    game = PuyoGame(state, size, sw, sh)
    while state.running:
        game.handle_events()
        game.update()
        game.draw()
    pygame.quit()

if __name__=='__main__':
    main()
