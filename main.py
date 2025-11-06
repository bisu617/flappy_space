import pygame
import random

pygame.init()

# Constants
WIDTH = 900
HEIGHT = 500
FPS = 60
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Flappy Space")
clock = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 20)

# Colors
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)
WHITE = (254, 254, 254)
SPACE_BLUE = (10, 10, 50)
STAR_YELLOW = (255, 255, 200)
NEON_GREEN = (57, 255, 20)
LAVA_RED = (255, 80, 0)

# Player properties
player_x = 200
player_y = HEIGHT // 2
player_width = 30
player_height = 30
y_velocity = 0
gravity = 0.5
jump_strength = -10
max_fall_speed = 10

# Obstacle properties
obstacles = [WIDTH + i * 300 for i in range(5)]
obstacle_heights = [random.randint(50, 300) for _ in range(5)]
gap = 150
speed = 3
score = 0
high_score = 0
game_over = False
game_started = False
passed_obstacles = [False for _ in obstacles]

# Background stars
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(100)]

# Audio setup with error handling
pygame.mixer.init()
try:
    pygame.mixer.music.load("beans.mp3")
    pygame.mixer.music.set_volume(0.2)
    music_available = True
except:
    print("Warning: beans.mp3 not found. Game will run without music.")
    music_available = False


def draw_player(x, y):
    """Draw the player spaceship and return its collision rect"""
    player_rect = pygame.Rect(x, y, player_width, player_height)
    pygame.draw.rect(screen, LAVA_RED, player_rect, 0, 12)
    pygame.draw.circle(screen, NEON_GREEN, (x + 25, y + 15), 12)
    pygame.draw.circle(screen, BLACK, (x + 24, y + 12), 5)
    return player_rect


def draw_obstacles(player_rect):
    """Draw obstacles and return True if collision detected"""
    collision = False
    for i in range(len(obstacles)):
        top_rect = pygame.Rect(obstacles[i], 0, 30, obstacle_heights[i])
        bottom_rect = pygame.Rect(obstacles[i], obstacle_heights[i] + gap, 30, 
                                 HEIGHT - (obstacle_heights[i] + gap))
        pygame.draw.rect(screen, CYAN, top_rect)
        pygame.draw.rect(screen, CYAN, bottom_rect)
        
        if player_rect.colliderect(top_rect) or player_rect.colliderect(bottom_rect):
            collision = True
    
    return collision


def draw_stars():
    """Draw and animate background stars"""
    for s in stars:
        pygame.draw.rect(screen, WHITE, (s[0], s[1], 3, 3))
        s[0] -= 0.5
        if s[0] < 0:
            s[0] = WIDTH
            s[1] = random.randint(0, HEIGHT)


def reset_game():
    """Reset all game variables to initial state"""
    global player_y, y_velocity, obstacles, obstacle_heights, passed_obstacles, score, game_over
    player_y = HEIGHT // 2
    y_velocity = 0
    obstacles = [WIDTH + i * 300 for i in range(5)]
    obstacle_heights = [random.randint(50, 300) for _ in range(5)]
    passed_obstacles = [False for _ in obstacles]
    score = 0
    game_over = False


# Main game loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(SPACE_BLUE)
    draw_stars()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_started:
                    game_started = True
                    if music_available:
                        pygame.mixer.music.play(-1)
                elif game_over:
                    reset_game()
                    if music_available:
                        pygame.mixer.music.play(-1)
                else:
                    y_velocity = jump_strength

    if game_started:
        # Apply gravity
        y_velocity += gravity
        if y_velocity > max_fall_speed:
            y_velocity = max_fall_speed
        player_y += y_velocity

        # Boundary checks
        if player_y < 0:
            player_y = 0
            y_velocity = 0
        if player_y > HEIGHT - player_height:
            player_y = HEIGHT - player_height
            game_over = True
            if music_available:
                pygame.mixer.music.stop()

        # Draw player
        player_rect = draw_player(player_x, player_y)

        # Update obstacles
        for i in range(len(obstacles)):
            if not game_over:
                obstacles[i] -= speed

                # Score when passing obstacle
                if not passed_obstacles[i] and player_x > obstacles[i] + 30:
                    score += 1
                    passed_obstacles[i] = True

                # Respawn obstacle when off-screen (improved logic)
                if obstacles[i] < -30:
                    # Find the rightmost obstacle
                    max_x = max(obstacles)
                    obstacles[i] = max_x + 300
                    obstacle_heights[i] = random.randint(50, 300)
                    passed_obstacles[i] = False

        # Check collisions
        if draw_obstacles(player_rect):
            game_over = True
            if music_available:
                pygame.mixer.music.stop()

        # Display score
        if score > high_score:
            high_score = score
        score_text = font.render(f"Score: {score}", True, WHITE)
        high_score_text = font.render(f"High Score: {high_score}", True, STAR_YELLOW)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 40))

        if game_over:
            over_text = font.render("Game Over! Press SPACE to restart", True, STAR_YELLOW)
            screen.blit(over_text, (200, HEIGHT // 2))
    else:
        start_text = font.render("Press SPACE to Start Flappy Space", True, STAR_YELLOW)
        screen.blit(start_text, (250, HEIGHT // 2))

    pygame.display.flip()

pygame.quit()