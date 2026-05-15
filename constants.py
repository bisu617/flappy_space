import pygame

# Screen settings
WIDTH = 900
HEIGHT = 500
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

# Level Configurations
LEVELS = {
    "Easy": {
        "speed": 3,
        "gap": 200,
        "gravity": 0.35,
        "jump": -8,
        "obstacle_dist": 350
    },
    "Intermediate": {
        "speed": 4,
        "gap": 160,
        "gravity": 0.5,
        "jump": -10,
        "obstacle_dist": 300
    },
    "Hard": {
        "speed": 6,
        "gap": 130,
        "gravity": 0.6,
        "jump": -11,
        "obstacle_dist": 250
    },
    "Impossible": {
        "speed": 9,
        "gap": 110,
        "gravity": 0.8,
        "jump": -13,
        "obstacle_dist": 200
    }
}

# Player settings
PLAYER_SIZE = 30
PLAYER_X = 200
MAX_FALL_SPEED = 12
