import pygame

# Screen settings
WIDTH = 1920
HEIGHT = 1080
FPS = 60

# Colors
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)
WHITE = (254, 254, 254)
SPACE_BLUE = (10, 10, 50)
STAR_YELLOW = (255, 255, 200)
NEON_GREEN = (57, 255, 20)
LAVA_RED = (255, 80, 0)
DARK_BLUE = (15, 15, 60)
GLASS_BG = (255, 255, 255, 30)  # For UI elements

# Game States
STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"
STATE_LEADERBOARD = "LEADERBOARD"
STATE_NAME_ENTRY = "NAME_ENTRY"

# Level Configurations (Scaled for 1080p)
LEVELS = {
    "Easy": {
        "speed": 6.5,
        "gap": 430,
        "gravity": 0.75,
        "jump": -17,
        "obstacle_dist": 750
    },
    "Intermediate": {
        "speed": 8.5,
        "gap": 345,
        "gravity": 1.1,
        "jump": -21.5,
        "obstacle_dist": 645
    },
    "Hard": {
        "speed": 13,
        "gap": 280,
        "gravity": 1.3,
        "jump": -23.5,
        "obstacle_dist": 540
    },
    "Impossible": {
        "speed": 19,
        "gap": 235,
        "gravity": 1.7,
        "jump": -28,
        "obstacle_dist": 430
    }
}

# Player settings
PLAYER_SIZE = 65
PLAYER_X = 430
MAX_FALL_SPEED = 25
