from constants import PUYO_TEXT, MIN_TILE_SIZE
from assets import nuisance_images

def ceildiv(a, b):
    """Returns the ceiling division of a by b."""
    return -(a // -b)

def calculate_tile_size(grid_w, grid_h, base_size, max_w, max_h, margin_w=5, margin_h=6):
    max_tile_w = max_w // (grid_w + margin_w)
    max_tile_h = max_h // (grid_h + margin_h)
    return max(min(max_tile_w, max_tile_h, base_size), MIN_TILE_SIZE)

def get_puyo_image(nuisance_count):
    images = []
    for value, img in sorted(nuisance_images.items(), reverse=True):
        while nuisance_count >= value:
            images.append(img)
            nuisance_count -= value
    return images

def get_puyo_text(nuisance_count):
    text = ""
    for value, char in sorted(PUYO_TEXT.items(), reverse=True):
        while nuisance_count >= value:
            text += char
            nuisance_count -= value
    return text