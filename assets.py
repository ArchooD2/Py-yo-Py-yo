import pygame
from constants import PUYO_EMOJIS

# Load these once
nuisance_images = {
    value: pygame.image.load(f"nuisance_images/{key}")
    for value, key in PUYO_EMOJIS.items()
}