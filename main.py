import pygame
import sys
import random
from pygame import mixer

pygame.init()
mixer.init()

Karel = pygame.image.load("Karel.png")
beeper = pygame.image.load("beeper.png")
mixer.music.load("maou_game_village10.ogg")

pygame.display.set_icon(Karel)

def play_music(music_file):
        mixer.music.load(music_file)
        mixer.music.play(-1)

def stop_music():
    mixer.music.stop()

you_did_it_screen_loop = [
    pygame.image.load("you_did_it_1.png"),
    pygame.image.load("you_did_it_2.png"),
    pygame.image.load("you_did_it_3.png"),
    pygame.image.load("you_did_it_4.png"),
    pygame.image.load("you_did_it_5.png"),
    pygame.image.load("you_did_it_6.png")
]

before_boss_screen_scene = [
    pygame.image.load("before_boss_1.png"),
    pygame.image.load("before_boss_2.png"),
    pygame.image.load("before_boss_3.png"),
    pygame.image.load("before_boss_4.png"),
    pygame.image.load("before_boss_5.png"),
    pygame.image.load("before_boss_6.png")
]

after_boss_screen_scene = [
    pygame.image.load("after_boss_1.png"),
    pygame.image.load("after_boss_2.png"),
    pygame.image.load("after_boss_3.png"),
    pygame.image.load("after_boss_4.png") 
]

title_music = "maou_game_village10.ogg"  
game_over_music = "maou_game_theme07.ogg" 
you_did_it_music = "maou_game_town05.ogg"  
boss_music = "maou_game_rock44.ogg"

play_music(title_music)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Karel Shooter")
        self.clock = pygame.time.Clock()

        
        self.title_screen = pygame.image.load("titlescreen.png")
        self.tutorial_screen = pygame.image.load("tutorial.png")
        self.credits_screen = pygame.image.load("credits.png")
        self.play_screen = pygame.image.load("backgroundkarel.png")
        self.you_did_it_screen = pygame.image.load("you_did_it.png")
        self.game_over_screen = pygame.image.load("game_over.png")
        self.before_boss_screen = pygame.image.load("before_boss.png")
        self.boss_play_screen = pygame.image.load("backgroundkarel.png")
        self.after_boss_screen = pygame.image.load("after_boss.png")

        self.current_screen = self.title_screen

        self.play_button = KarelButton("play_button.png", 500, 200)
        self.tutorial_button = KarelButton("tutorial_button.png", 500, 300)
        self.credits_button = KarelButton("credits_button.png", 500, 400)
        self.back_button = KarelButton("back_button.png", 250, 450)
        self.buttons = [self.play_button, self.tutorial_button, self.credits_button]
        self.karel_position = (0, 450)
        self.karel_movable = False
        self.running = True
        self.beepers = []
        self.enemies = []
        self.powerups = []
        self.score = 0
        self.paused = False
        self.game_music = "maou_game_village10.ogg"

    def run(self):
        while self.running:
            self.handle_events()
            if not self.paused and self.current_screen != self.game_over_screen:  # Add condition for game over screen
                self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in self.buttons + [self.back_button]:
                        if button.is_clickable and button.is_clicked(event.pos):
                            self.handle_button_click(button)
                    if self.current_screen == self.play_screen:
                        self.shoot_beeper()
                    elif self.current_screen == self.boss_play_screen:
                        self.shoot_beeper()
            elif event.type == pygame.MOUSEMOTION:
                if self.karel_movable:
                    self.handle_mouse_motion(event.pos)

    def handle_button_click(self, button):
        if button == self.tutorial_button:
            self.current_screen = self.tutorial_screen
            self.disable_buttons()
        elif button == self.credits_button:
            self.current_screen = self.credits_screen
            self.disable_buttons()
        elif button == self.play_button:
            self.current_screen = self.play_screen
            self.enable_karel_movement()
            self.enemies = self.create_enemies()
            self.powerups = self.create_powerups()
            self.disable_buttons()
        elif button == self.back_button:
            if self.current_screen != self.play_screen and self.current_screen != self.boss_play_screen:
                self.current_screen = self.title_screen
                self.enable_buttons()
                self.karel_movable = False
                self.enemies = []
                self.powerups = []
                self.score = 0

    def disable_buttons(self):
        for button in self.buttons:
            button.is_clickable = False
        self.back_button.is_clickable = True

    def enable_buttons(self):
        for button in self.buttons:
            button.is_clickable = True
        self.back_button.is_clickable = False

    def enable_karel_movement(self):
        self.karel_movable = True

    def handle_mouse_motion(self, pos):
        new_x = pos[0]
        new_x = max(0, min(new_x, 800 - Karel.get_width()))
        self.karel_position = (new_x, self.karel_position[1])

    def update(self):
        self.update_beepers()
        if self.current_screen == self.play_screen:
            self.update_enemies()
            self.update_powerups()
            self.check_collisions()
        elif self.current_screen == self.you_did_it_screen:
            self.update_you_did_it_screen()
        elif self.current_screen == self.before_boss_screen:
            self.update_before_boss_screen()
        elif self.current_screen == self.boss_play_screen:
            self.back_button.is_clickable = False
            self.enable_karel_movement()
            self.update_enemies()
            self.update_powerups()
            self.disable_buttons()
            self.check_collisions()
        elif self.current_screen == self.after_boss_screen:
            self.update_after_boss_screen()

    def update_beepers(self):
        for beeper in self.beepers:
            beeper.update()
            if beeper.rect.top <= 0:
                self.beepers.remove(beeper)

    def update_enemies(self):
        for enemy in self.enemies:
            enemy.update()
            if enemy.rect.top >= 600:
                self.enemies.remove(enemy)
                self.enemies.append(self.create_enemy())
                
    def update_powerups(self):
        for powerup in self.powerups:
            powerup.update()
            if powerup.rect.top >= 600:
                self.powerups.remove(powerup)
                self.powerups.append(self.create_powerup())

    def check_collisions(self):
        for beeper in self.beepers:
            for enemy in self.enemies:
                if beeper.rect.colliderect(enemy.rect):
                    self.beepers.remove(beeper)
                    self.enemies.remove(enemy)
                    self.enemies.append(self.create_enemy())
                    self.score += 10
                    break
                
        for beeper in self.beepers:
            for powerup in self.powerups:
                if beeper.rect.colliderect(powerup.rect):
                    self.beepers.remove(beeper)
                    self.powerups.remove(powerup)
                    self.powerups.append(self.create_powerup())
                    self.score += 20
                    break

        for enemy in self.enemies:
            if enemy.rect.bottom >= 600:
                self.current_screen = self.game_over_screen
                stop_music()
                play_music(game_over_music)
                self.back_button.is_clickable = False
        """
        if self.score >= 2000:
            self.current_screen = self.you_did_it_screen
            stop_music()
            play_music(you_did_it_music)

            self.you_did_it_start_time = pygame.time.get_ticks()
            self.you_did_it_frame = 0
        """       
        if self.score >= 2000 and self.current_screen == self.play_screen:
            self.score = 0
            self.current_screen = self.before_boss_screen
            stop_music()
            self.before_boss_frame = 0
            self.before_boss_start_time = pygame.time.get_ticks()
        
        elif self.score >= 3000 and self.current_screen == self.boss_play_screen:
            self.score = 0
            self.current_screen = self.after_boss_screen
            stop_music()
            self.after_boss_frame = 0
            self.after_boss_start_time = pygame.time.get_ticks()
            
    def update_you_did_it_screen(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.you_did_it_start_time > 500:  
            self.you_did_it_start_time = current_time
            self.you_did_it_frame = (self.you_did_it_frame + 1) % len(you_did_it_screen_loop)
    
    def update_before_boss_screen(self):
        if self.before_boss_frame < len(before_boss_screen_scene):
            current_time = pygame.time.get_ticks()
            if current_time - self.before_boss_start_time > 3000:  
                self.before_boss_frame += 1
                self.before_boss_start_time = pygame.time.get_ticks()
                if self.before_boss_frame == 6:
                    self.current_screen = self.boss_play_screen
                    play_music(boss_music)
                    self.enable_karel_movement()
                    self.disable_buttons()
    
    def update_after_boss_screen(self):
        if self.after_boss_frame < len(after_boss_screen_scene):
            current_time = pygame.time.get_ticks()
            if current_time - self.after_boss_start_time > 3000:  
                self.after_boss_frame += 1
                self.after_boss_start_time = pygame.time.get_ticks()
                if self.after_boss_frame == 4:
                    self.you_did_it_start_time = pygame.time.get_ticks()
                    self.you_did_it_frame = 0
                    play_music(you_did_it_music)
                    self.current_screen = self.you_did_it_screen

    def draw(self):
        self.screen.blit(self.current_screen, (0, 0))
        if self.current_screen in [self.tutorial_screen, self.credits_screen]:
            self.back_button.draw(self.screen)
        for button in self.buttons:
            if button.is_clickable:
                button.draw(self.screen)
        if self.current_screen == self.play_screen:
            self.screen.blit(Karel, self.karel_position)
            for beeper in self.beepers:
                beeper.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for powerup in self.powerups:
                powerup.draw(self.screen)
            self.draw_score()
        elif self.current_screen == self.boss_play_screen:
            self.screen.blit(Karel, self.karel_position)
            for beeper in self.beepers:
                beeper.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for powerup in self.powerups:
                powerup.draw(self.screen)
            self.draw_score()
        elif self.current_screen == self.you_did_it_screen:
            self.screen.blit(you_did_it_screen_loop[self.you_did_it_frame], (0, 0))
        elif self.current_screen == self.game_over_screen:
            self.draw_game_over_score()
        elif self.current_screen == self.before_boss_screen:
            if self.before_boss_frame < len(before_boss_screen_scene):
                self.screen.blit(before_boss_screen_scene[self.before_boss_frame], (0, 0))
        elif self.current_screen == self.after_boss_screen:
            if self.after_boss_frame < len(after_boss_screen_scene):
                self.screen.blit(after_boss_screen_scene[self.after_boss_frame], (0, 0))
        

    def draw_score(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))

    def draw_game_over_score(self):
        font = pygame.font.Font(None, 48)
        score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
        score_rect = score_text.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(score_text, score_rect)

    def shoot_beeper(self):
        beeper = Beeper(self.karel_position[0] + Karel.get_width() // 2, self.karel_position[1])
        self.beepers.append(beeper)

    def create_enemies(self):
        return [self.create_enemy() for _ in range(6)]
    
    def create_powerups(self):
        return [self.create_powerup() for _ in range(1)]

    def create_enemy(self):
        x = random.randint(0, 600)
        y = random.randint(-600, -50)
        speed = 3
        return Enemy(x, y, speed)
    
    def create_powerup(self):
        x = random.randint(0, 600)
        y = random.randint(-600, -50)
        speed = 25
        return Powerup(x, y, speed)

class KarelButton:
    def __init__(self, image, x, y):
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.is_clickable = True

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Beeper:
    def __init__(self, x, y):
        self.image = beeper
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = -10

    def update(self):
        self.rect.y += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Enemy:
    def __init__(self, x, y, speed):
        self.rect = pygame.Rect(x, y, 100, 100)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

    def draw(self, surface):
        pygame.draw.ellipse(surface, (255, 0, 0), self.rect)
        pygame.draw.ellipse(surface, (0, 0, 0), self.rect, 5)

class Powerup:
    def __init__(self, x, y, speed):
        self.rect = pygame.Rect(x, y, 100, 100)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

    def draw(self, surface):
        pygame.draw.ellipse(surface, (255, 255, 0), self.rect)
        pygame.draw.ellipse(surface, (0, 0, 0), self.rect, 5)

if __name__ == "__main__":
    game = Game()
    game.run()

pygame.quit()
sys.exit()
