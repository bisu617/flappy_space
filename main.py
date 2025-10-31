import pygame
import random

pygame.init()


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
GRAY = (128, 128, 128)
SPACE_BLUE  = (10, 10, 50)
STAR_YELLOW = (255, 255, 200)
NEON_GREEN  = (57, 255, 20)
LAVA_RED    = (255, 80, 0)
OBSTACLE_COLOR = (40, 40, 70)


player_x = 200
player_y = HEIGHT // 2
player_width = 30
player_height = 30
y_velocity = 0
gravity = 0.5
jump_strength = -10
max_fall_speed = 10


obstacles = [WIDTH + i * 300 for i in range(5)]  # x positions
obstacle_heights = [random.randint(50, 300) for _ in range(5)]
gap = 150
speed = 3
score = 0
high_score = 0
game_over = False
game_started = False


passed_obstacles = [False for _ in obstacles]


stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(100)]


pygame.mixer.init()
pygame.mixer.music.load("beans.mp3")
pygame.mixer.music.set_volume(0.2)


def draw_player(x, y):
    player_rect = pygame.Rect(x, y, player_width, player_height)
    pygame.draw.rect(screen, LAVA_RED, player_rect, 0, 12)
    pygame.draw.circle(screen, NEON_GREEN, (x + 25, y + 15), 12)
    pygame.draw.circle(screen, BLACK, (x + 24, y + 12), 5)
    return player_rect

def draw_obstacles():
    global game_over
    for i in range(len(obstacles)):
        top_rect = pygame.Rect(obstacles[i], 0, 30, obstacle_heights[i])
        bottom_rect = pygame.Rect(obstacles[i], obstacle_heights[i] + gap, 30, HEIGHT - (obstacle_heights[i] + gap))
        pygame.draw.rect(screen, CYAN, top_rect)
        pygame.draw.rect(screen, CYAN, bottom_rect)
        if player_rect.colliderect(top_rect) or player_rect.colliderect(bottom_rect):
            game_over = True
            pygame.mixer.music.stop()  

def draw_stars():
    for s in stars:
        pygame.draw.rect(screen, WHITE, (s[0], s[1], 3, 3))
        s[0] -= 0.5
        if s[0] < 0:
            s[0] = WIDTH
            s[1] = random.randint(0, HEIGHT)

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
                    pygame.mixer.music.play(-1)  
                elif game_over:
                    # Reset game
                    player_y = HEIGHT // 2
                    y_velocity = 0
                    obstacles = [WIDTH + i * 300 for i in range(5)]
                    obstacle_heights = [random.randint(50, 300) for _ in range(5)]
                    passed_obstacles = [False for _ in obstacles]  
                    score = 0
                    game_over = False
                    pygame.mixer.music.play(-1)  
                else:
                    y_velocity = jump_strength

    if game_started:
       
        y_velocity += gravity
        if y_velocity > max_fall_speed:
            y_velocity = max_fall_speed
        player_y += y_velocity

       
        if player_y < 0:
            player_y = 0
            y_velocity = 0
        if player_y > HEIGHT - player_height:
            player_y = HEIGHT - player_height
            game_over = True
            pygame.mixer.music.stop()  

       
        player_rect = draw_player(player_x, player_y)

       
        for i in range(len(obstacles)):
            if not game_over:
                obstacles[i] -= speed

              
                if not passed_obstacles[i] and player_x > obstacles[i] + 30:
                    score += 1
                    passed_obstacles[i] = True

              
                if obstacles[i] < -30:
                    obstacles[i] = obstacles[i - 1] + 300
                    obstacle_heights[i] = random.randint(50, 300)
                    passed_obstacles[i] = False

        draw_obstacles()

        
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
