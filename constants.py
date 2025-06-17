import pygame

DEFAULT_GRID_WIDTH = 6
DEFAULT_GRID_HEIGHT = 12
BASE_TILE_SIZE = 40
FPS = 60
MAX_SCREEN_WIDTH = 1920
MAX_SCREEN_HEIGHT = 1080
MIN_TILE_SIZE = 15

COLORS = ["red", "green", "blue", "yellow"]
EMPTY = None
POP_TIME = 0.7

CHAIN_BONUS = [0, 8, 16, 32, 64, 96, 128, 160, 192, 224, 256]
COLOR_BONUS = [0, 3, 6, 12, 24]
GROUP_BONUS = [0, 2, 3, 4, 5, 6, 7, 10]

COLOR_MAP = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    EMPTY: (0, 0, 0),
}

# Mapping for puyo emojis
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
    1: "◯",  # Small Garbage Puyo
    6: "⚪",  # Large Garbage Puyo (6 small ones)
    30: "♪",  # Red nuisance puyo (rock)
    90: "⭐",  # Star Puyo
    180: "🌙",  # Moon Puyo
    360: "☄️",  # Comet Puyo
    720: "💠",  # Saturn Puyo
    1000: "🃏",  # Club Puyo
    5000: "💎",  # Diamond Puyo
    20000: "❤️",  # Heart Puyo
    100000: "♠️",  # Spade Puyo
    500000: "👑",  # Crown Puyo
    2000000: "🍄",  # Mushroom Puyo
    10000000: "☀️",  # Sun Puyo
    50000000: "🍅",  # Top Hat Puyo
    200000000: "⚽",  # Ball Puyo
    1000000000: "🎪",  # Tent Puyo
    5000000000: "💿",  # GD-ROM Puyo
    10000000000: "🔵",  # Blue Swirl Puyo
    50000000000: "🟢",  # Green Swirl Puyo
    100000000000: "🟡",  # Yellow Swirl Puyo
    500000000000: "🟣",  # Purple Swirl Puyo
    1000000000000: "🔴",  # Red Swirl Puyo
}