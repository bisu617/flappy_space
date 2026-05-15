import pygame
import random
import sys
from constants import *
import database
import threading
import asyncio

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Flappy Space: Enhanced Edition")
        self.clock = pygame.time.Clock()
        self.font_main = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 18)
        
        # Enable key repetition for better text input
        pygame.key.set_repeat(400, 50)
        
        self.player_name = ""
        self.load_user_data() 
        
        self.level = "Intermediate"
        self.score = 0
        self.high_score = 0
        self.leaderboard_data = []
        self.submitting = False
        self.playing_started = False
        self.input_active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # If we already have a name, go straight to menu
        if self.player_name:
            self.state = STATE_MENU
        else:
            self.state = STATE_NAME_ENTRY
        
        # Game objects
        self.player_y = HEIGHT // 2
        self.y_velocity = 0
        self.obstacles = []
        self.obstacle_heights = []
        self.passed_obstacles = []
        self.stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(100)]
        
        # Audio
        pygame.mixer.init()
        try:
            pygame.mixer.music.load("beans.mp3")
            pygame.mixer.music.set_volume(0.2)
            self.music_enabled = True
        except:
            self.music_enabled = False
            
        self.reset_game()

    def reset_game(self):
        config = LEVELS[self.level]
        self.player_y = HEIGHT // 2
        self.y_velocity = 0
        self.score = 0
        self.obstacles = [WIDTH + i * config["obstacle_dist"] for i in range(5)]
        self.obstacle_heights = [random.randint(50, 300) for _ in range(5)]
        self.passed_obstacles = [False for _ in range(5)]
        self.playing_started = False

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Key support
            if event.type == pygame.KEYDOWN:
                if self.state == STATE_MENU:
                    if event.key == pygame.K_SPACE:
                        self.start_game()
                    if event.key == pygame.K_l:
                        self.show_leaderboard()
                    if event.key in [pygame.K_1, pygame.K_KP1]: 
                        self.level = "Easy"
                        self.start_game()
                    if event.key in [pygame.K_2, pygame.K_KP2]: 
                        self.level = "Intermediate"
                        self.start_game()
                    if event.key in [pygame.K_3, pygame.K_KP3]: 
                        self.level = "Hard"
                        self.start_game()
                    if event.key in [pygame.K_4, pygame.K_KP4]: 
                        self.level = "Impossible"
                        self.start_game()
                
                elif self.state == STATE_PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.jump()
                
                elif self.state == STATE_GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        self.start_game()
                    if event.key == pygame.K_m:
                        self.state = STATE_MENU
                    if event.key == pygame.K_s and not self.submitting:
                        self.submit_score()
                
                elif self.state == STATE_LEADERBOARD:
                    if event.key in [pygame.K_ESCAPE, pygame.K_m]:
                        self.state = STATE_MENU
                
                elif self.state == STATE_NAME_ENTRY:
                    if event.key == pygame.K_RETURN and len(self.player_name) > 0:
                        self.save_user_data() # Save the name!
                        self.state = STATE_MENU
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.key == pygame.K_a and (event.mod & pygame.KMOD_CTRL):
                        self.player_name = "" # Clear for Ctrl+A
                    elif event.key == pygame.K_DELETE:
                        self.player_name = ""
                    elif event.unicode.isprintable():
                        if len(self.player_name) < 15:
                            self.player_name += event.unicode

                # Username Typing Logic in Menu
                if self.input_active and self.state == STATE_MENU:
                    if event.key == pygame.K_RETURN:
                        self.save_user_data() # Save if changed in menu
                        self.input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.key == pygame.K_a and (event.mod & pygame.KMOD_CTRL):
                        self.player_name = ""
                    elif event.key == pygame.K_DELETE:
                        self.player_name = ""
                    elif event.unicode.isprintable():
                        if len(self.player_name) < 15:
                            self.player_name += event.unicode

            # Mouse / Touch support
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                
                if self.state == STATE_MENU:
                    # Check Name Input Box
                    name_rect = pygame.Rect(WIDTH // 2 - 100, 240, 200, 35)
                    if name_rect.collidepoint(mx, my):
                        self.input_active = True
                        return
                    else:
                        self.input_active = False

                    # Check level buttons
                    y_off = 300
                    for i, lvl in enumerate(LEVELS.keys()):
                        rect = pygame.Rect(WIDTH // 2 - 100, y_off + i * 45, 200, 40)
                        if rect.collidepoint(mx, my):
                            self.level = lvl
                            self.start_game()
                            return
                    
                    # Check leaderboard button (roughly where 'L' is mentioned)
                    if my > 450:
                        self.show_leaderboard()
                        return

                    # If not button, start game
                    self.start_game()
                
                elif self.state == STATE_PLAYING:
                    self.jump()
                
                elif self.state == STATE_GAME_OVER:
                    self.start_game()
                
                elif self.state == STATE_LEADERBOARD:
                    self.state = STATE_MENU

    def jump(self):
        self.playing_started = True
        self.y_velocity = LEVELS[self.level]["jump"]

    def start_game(self):
        self.reset_game()
        self.state = STATE_PLAYING
        if self.music_enabled: pygame.mixer.music.play(-1)

    def show_leaderboard(self):
        self.state = STATE_LEADERBOARD
        self.leaderboard_data = [] # Show loading
        
        def fetch():
            data = database.get_top_scores(level=self.level, limit=50)
            # Filter unique users (keep highest score)
            unique_data = {}
            for entry in data:
                user = entry['username']
                if user not in unique_data or entry['score'] > unique_data[user]['score']:
                    unique_data[user] = entry
            
            # Sort and take top 10
            sorted_data = sorted(unique_data.values(), key=lambda x: x['score'], reverse=True)
            self.leaderboard_data = sorted_data[:10]
            
        threading.Thread(target=fetch, daemon=True).start()

    def submit_score(self):
        if self.score <= 0: return
        self.submitting = True
        
        def task():
            database.submit_score(self.player_name, self.score, self.level)
            self.submitting = False
            
        threading.Thread(target=task, daemon=True).start()

    def update(self):
        # Update cursor blink
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
            
        if self.state == STATE_PLAYING and self.playing_started:
            config = LEVELS[self.level]
            
            # Apply physics
            self.y_velocity += config["gravity"]
            if self.y_velocity > MAX_FALL_SPEED:
                self.y_velocity = MAX_FALL_SPEED
            self.player_y += self.y_velocity
            
            # Boundary checks
            if self.player_y < 0:
                self.player_y = 0
                self.y_velocity = 0
            if self.player_y > HEIGHT - PLAYER_SIZE:
                self.game_over()
            
            # Update obstacles
            for i in range(len(self.obstacles)):
                self.obstacles[i] -= config["speed"]
                
                # Scoring
                if not self.passed_obstacles[i] and PLAYER_X > self.obstacles[i] + 30:
                    self.score += 1
                    self.passed_obstacles[i] = True
                    
                # Respawn
                if self.obstacles[i] < -30:
                    max_x = max(self.obstacles)
                    self.obstacles[i] = max_x + config["obstacle_dist"]
                    self.obstacle_heights[i] = random.randint(50, 300)
                    self.passed_obstacles[i] = False
            
            # Check collisions
            player_rect = pygame.Rect(PLAYER_X, self.player_y, PLAYER_SIZE, PLAYER_SIZE)
            for i in range(len(self.obstacles)):
                top_rect = pygame.Rect(self.obstacles[i], 0, 30, self.obstacle_heights[i])
                bottom_rect = pygame.Rect(self.obstacles[i], self.obstacle_heights[i] + config["gap"], 30, HEIGHT)
                if player_rect.colliderect(top_rect) or player_rect.colliderect(bottom_rect):
                    self.game_over()

    def game_over(self):
        self.state = STATE_GAME_OVER
        if self.score > self.high_score:
            self.high_score = self.score
        
        # Auto-submit score
        if self.score > 0:
            self.submit_score()
            
        if self.music_enabled:
            pygame.mixer.music.stop()

    def save_user_data(self):
        try:
            import json
            with open("user_prefs.json", "w") as f:
                json.dump({"name": self.player_name}, f)
        except:
            pass

    def load_user_data(self):
        try:
            import json
            import os
            if os.path.exists("user_prefs.json"):
                with open("user_prefs.json", "r") as f:
                    data = json.load(f)
                    self.player_name = data.get("name", "")
        except:
            self.player_name = ""

    def draw_stars(self):
        for s in self.stars:
            pygame.draw.rect(self.screen, WHITE, (s[0], s[1], 2, 2))
            s[0] -= 0.5
            if s[0] < 0:
                s[0] = WIDTH
                s[1] = random.randint(0, HEIGHT)

    def draw_ui_button(self, text, x, y, w, h, active=False):
        color = CYAN if active else DARK_BLUE
        pygame.draw.rect(self.screen, color, (x, y, w, h), border_radius=8)
        pygame.draw.rect(self.screen, WHITE, (x, y, w, h), 2, border_radius=8)
        txt = self.font_main.render(text, True, WHITE if not active else BLACK)
        self.screen.blit(txt, (x + (w - txt.get_width()) // 2, y + (h - txt.get_height()) // 2))

    def draw(self):
        self.screen.fill(SPACE_BLUE)
        self.draw_stars()
        
        if self.state == STATE_MENU:
            title = self.font_title.render("FLAPPY SPACE", True, CYAN)
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
            
            instr = self.font_main.render("Press SPACE to Start", True, WHITE)
            self.screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, 190))
            
            # Name Input Field
            name_label = self.font_small.render("PLAYER NAME (CLICK TO EDIT):", True, STAR_YELLOW)
            self.screen.blit(name_label, (WIDTH // 2 - name_label.get_width() // 2, 230))
            
            name_rect = pygame.Rect(WIDTH // 2 - 100, 255, 200, 35)
            pygame.draw.rect(self.screen, CYAN if self.input_active else DARK_BLUE, name_rect, border_radius=5)
            pygame.draw.rect(self.screen, WHITE, name_rect, 2, border_radius=5)
            
            name_txt = self.font_main.render(self.player_name, True, WHITE)
            self.screen.blit(name_txt, (WIDTH // 2 - name_txt.get_width() // 2, 258))

            # Level Selection UI
            y_off = 310
            for i, lvl in enumerate(LEVELS.keys()):
                self.draw_ui_button(lvl, WIDTH // 2 - 100, y_off + i * 42, 200, 38, self.level == lvl)
            
            help_txt = self.font_small.render("Use numbers 1-4 to select level | L for Leaderboard", True, STAR_YELLOW)
            self.screen.blit(help_txt, (WIDTH // 2 - help_txt.get_width() // 2, 480))

        elif self.state == STATE_PLAYING or self.state == STATE_GAME_OVER:
            # Draw obstacles
            config = LEVELS[self.level]
            for i in range(len(self.obstacles)):
                pygame.draw.rect(self.screen, CYAN, (self.obstacles[i], 0, 30, self.obstacle_heights[i]))
                pygame.draw.rect(self.screen, CYAN, (self.obstacles[i], self.obstacle_heights[i] + config["gap"], 30, HEIGHT))
            
            # Draw player
            pygame.draw.rect(self.screen, LAVA_RED, (PLAYER_X, self.player_y, PLAYER_SIZE, PLAYER_SIZE), border_radius=8)
            pygame.draw.circle(self.screen, NEON_GREEN, (PLAYER_X + 25, self.player_y + 15), 10)
            pygame.draw.circle(self.screen, BLACK, (PLAYER_X + 25, self.player_y + 15), 4)
            
            # HUD
            score_txt = self.font_main.render(f"Score: {self.score}", True, WHITE)
            lvl_txt = self.font_small.render(f"Level: {self.level}", True, STAR_YELLOW)
            self.screen.blit(score_txt, (20, 20))
            self.screen.blit(lvl_txt, (20, 50))
            
            if self.state == STATE_PLAYING and not self.playing_started:
                hint_txt = self.font_main.render("CLICK OR SPACE TO JUMP!", True, WHITE)
                self.screen.blit(hint_txt, (WIDTH // 2 - hint_txt.get_width() // 2, HEIGHT // 2 + 50))
            
            if self.state == STATE_GAME_OVER:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.screen.blit(overlay, (0, 0))
                
                over_txt = self.font_title.render("GAME OVER", True, LAVA_RED)
                score_final = self.font_main.render(f"Final Score: {self.score}", True, WHITE)
                best_txt = self.font_main.render(f"High Score: {self.high_score}", True, STAR_YELLOW)
                
                status = "Score Saved!" if self.score > 0 else ""
                submit_txt = self.font_main.render(status, True, NEON_GREEN)
                restart_txt = self.font_main.render("Press SPACE to Restart", True, WHITE)
                menu_txt = self.font_small.render("Press M for Main Menu", True, WHITE)
                
                self.screen.blit(over_txt, (WIDTH // 2 - over_txt.get_width() // 2, 120))
                self.screen.blit(score_final, (WIDTH // 2 - score_final.get_width() // 2, 190))
                self.screen.blit(best_txt, (WIDTH // 2 - best_txt.get_width() // 2, 230))
                self.screen.blit(submit_txt, (WIDTH // 2 - submit_txt.get_width() // 2, 300))
                self.screen.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, 380))
                self.screen.blit(menu_txt, (WIDTH // 2 - menu_txt.get_width() // 2, 430))

        elif self.state == STATE_LEADERBOARD:
            title = self.font_title.render(f"TOP {self.level.upper()}S", True, STAR_YELLOW)
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
            
            if not self.leaderboard_data:
                msg = self.font_main.render(f"No scores yet for {self.level}", True, WHITE)
                self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 200))
            else:
                for i, entry in enumerate(self.leaderboard_data):
                    txt = self.font_main.render(f"{i+1}. {entry['username']} - {entry['score']}", True, WHITE)
                    self.screen.blit(txt, (WIDTH // 2 - 120, 130 + i * 30))
            
            back_txt = self.font_small.render("Press M to go back", True, CYAN)
            self.screen.blit(back_txt, (WIDTH // 2 - back_txt.get_width() // 2, 450))

        elif self.state == STATE_NAME_ENTRY:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill(SPACE_BLUE)
            self.screen.blit(overlay, (0, 0))
            self.draw_stars()
            
            title = self.font_title.render("WELCOME EXPLORER", True, CYAN)
            prompt = self.font_main.render("Identify yourself, Pilot:", True, WHITE)
            
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))
            self.screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 200))
            
            # Sleek Input Box
            name_rect = pygame.Rect(WIDTH // 2 - 200, 250, 400, 60)
            pygame.draw.rect(self.screen, DARK_BLUE, name_rect, border_radius=15)
            pygame.draw.rect(self.screen, CYAN if self.cursor_visible else WHITE, name_rect, 3, border_radius=15)
            
            # Render name with cursor
            display_name = self.player_name + ("|" if self.cursor_visible else "")
            name_txt = self.font_title.render(display_name, True, WHITE)
            self.screen.blit(name_txt, (WIDTH // 2 - name_txt.get_width() // 2, 255))
            
            instr = self.font_small.render("Press ENTER to verify and start mission", True, STAR_YELLOW)
            self.screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, 340))

        pygame.display.flip()

    async def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            await asyncio.sleep(0) # Required for web

if __name__ == "__main__":
    game = Game()
    asyncio.run(game.run())
