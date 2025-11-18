import pygame
from random import randint, choice
from math import sqrt

WIDTH = 800
HEIGHT = 600

pygame.mixer.init()

GAME_STATE = "MENU"
sound_enabled = True

def generate_beep(frequency=440, duration=0.08, volume=0.3):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = bytearray()
    for i in range(n_samples):
        value = int(128 + volume * 127 * (
            1.0 if (int(frequency * i / sample_rate * 2) % 2 == 0) else -1.0
        ))
        buf.append(max(0, min(255, value)))
    return pygame.mixer.Sound(buffer=bytes(buf))

hit_sound = generate_beep(600, 0.08, 0.4)
menu_sound = generate_beep(350, 0.08, 0.3)


def create_sprite(color, w, h, border_radius=6):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (0, 0, w, h), border_radius=border_radius)
    pygame.draw.rect(surf, (255, 255, 255), (w // 4, h // 4, w // 8, h // 8))
    pygame.draw.rect(surf, (255, 255, 255),
                     (w * 3 // 4 - w // 8, h // 4, w // 8, h // 8))
    return surf

def sprite_animation(color1, color2, w, h):
    return [create_sprite(color1, w, h), create_sprite(color2, w, h)]

class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.font = pygame.font.SysFont("Arial", 28)
        self._mouse_prev = False

    def draw(self, screen_surf):
        mouse = pygame.mouse.get_pos()
        color = (100, 100, 100) if self.rect.collidepoint(mouse) else (60, 60, 60)
        pygame.draw.rect(screen_surf, color, self.rect, border_radius=8)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        screen_surf.blit(text_surf, (
            self.rect.x + (self.rect.w - text_surf.get_width()) // 2,
            self.rect.y + (self.rect.h - text_surf.get_height()) // 2))

    def is_clicked(self):
        mouse = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()[0]
        clicked = pressed and (not self._mouse_prev) and self.rect.collidepoint(mouse)
        self._mouse_prev = pressed
        return clicked


class Hero:
    def __init__(self):
        self.start_x = WIDTH // 2
        self.start_y = HEIGHT // 2
        self.x = self.start_x
        self.y = self.start_y
        self.speed = 3
        self.anim_idle = sprite_animation((0, 180, 255), (0, 140, 255), 40, 40)
        self.anim_walk = sprite_animation((0, 255, 180), (0, 220, 140), 40, 40)
        self.current = self.anim_idle
        self.frame = 0
        self.timer = 0

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.current = self.anim_idle
        self.frame = 0
        self.timer = 0

    def update(self):
        moving = False
        if keyboard.left:
            self.x -= self.speed; moving = True
        if keyboard.right:
            self.x += self.speed; moving = True
        if keyboard.up:
            self.y -= self.speed; moving = True
        if keyboard.down:
            self.y += self.speed; moving = True

        self.x = max(0, min(WIDTH - 40, self.x))
        self.y = max(0, min(HEIGHT - 40, self.y))

        self.current = self.anim_walk if moving else self.anim_idle
        self.timer += 1
        if self.timer % 12 == 0:
            self.frame = (self.frame + 1) % 2

    def draw(self, surf):
        surf.blit(self.current[self.frame], (self.x, self.y))

class Enemy:
    def __init__(self, x, y, etype="patrol"):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.type = etype

        self.speed = 1.8 if etype == "chaser" else 1.2

        self.range_left = x - 80
        self.range_right = x + 80
        self.direction = 1

        self.anim_idle = sprite_animation((255, 80, 80), (255, 40, 40), 35, 35)
        self.anim_walk = sprite_animation((255, 160, 80), (255, 130, 40), 35, 35)
        self.frame = 0
        self.timer = 0

    def update(self, hero):
        if self.type == "static":
            pass
        elif self.type == "chaser":
            dx = hero.x - self.x
            dy = hero.y - self.y
            dist = sqrt(dx * dx + dy * dy)
            if dist < 240 and dist > 1:
                self.x += self.speed * (dx / dist)
                self.y += self.speed * (dy / dist)
        else:
            self.x += self.direction * self.speed
            if self.x > self.range_right:
                self.direction = -1
            if self.x < self.range_left:
                self.direction = 1

        self.timer += 1
        if self.timer % 18 == 0:
            self.frame = (self.frame + 1) % 2

    def draw(self, surf):
        surf.blit(self.anim_walk[self.frame], (self.x, self.y))


def random_enemy_bundle():
    enemies = []
    types = ["static", "patrol", "chaser"]

    chasers = 0

    for _ in range(6):
        x = randint(40, WIDTH - 40)
        y = randint(40, HEIGHT - 40)
        et = choice(types)

        if chasers < 2:
            et = "chaser"
            chasers += 1

        enemies.append(Enemy(x, y, et))

    return enemies

hero = Hero()
enemies = []
spawn_timer = 0
score = 0


switch_timer = 0
switch_interval = randint(300, 600)   

btn_start = Button("Start", 300, 200, 200, 50)
btn_sound = Button("Som Ligado", 300, 280, 200, 50)
btn_exit = Button("Sair", 300, 360, 200, 50)


def reset_game():
    global enemies, score, GAME_STATE, spawn_timer
    hero.reset()
    enemies = []
    score = 0
    spawn_timer = 0
    GAME_STATE = "MENU"


def draw():
    screen.clear()
    surf = screen.surface

    if GAME_STATE == "MENU":
        screen.fill((20, 20, 20))
        screen.draw.text("Sobreviva aos inimigos!",
                         center=(WIDTH // 2, 100),
                         fontsize=44, color="white")
        btn_start.draw(surf)
        btn_sound.draw(surf)
        btn_exit.draw(surf)

    elif GAME_STATE == "GAME":
        screen.fill((28, 28, 32))
        hero.draw(surf)
        for e in enemies:
            e.draw(surf)
        screen.draw.text(f"Pontuação: {int(score)}", (10, 10), color="white", fontsize=32)


def update():
    global GAME_STATE, sound_enabled, score, enemies, spawn_timer

    if GAME_STATE == "MENU":
        if btn_start.is_clicked():
            if sound_enabled: menu_sound.play()
            hero.reset()
            enemies = []
            score = 0
            spawn_timer = 0
            GAME_STATE = "GAME"

        if btn_sound.is_clicked():
            sound_enabled = not sound_enabled
            btn_sound.text = "Som ligado" if sound_enabled else "Som desligado"

        if btn_exit.is_clicked():
            raise SystemExit

    elif GAME_STATE == "GAME":


        
        if len(enemies) == 0:
            spawn_timer += 1
            if spawn_timer >= 60:   
                enemies = random_enemy_bundle()

        hero.update()
        score += 1
       
        
        global switch_timer, switch_interval

        switch_timer += 1
        if switch_timer >= switch_interval and enemies:
            switch_timer = 0
            switch_interval = randint(300, 600)  

            e = choice(enemies)

            if e.type == "static":
                e.type = "chaser"
                e.speed = 1.8
            else:
                e.type = "static"
                e.speed = 0
        
        for e in enemies:
            e.update(hero)

            if abs((hero.x + 20) - (e.x + 17)) < 28 and abs((hero.y + 20) - (e.y + 17)) < 28:
                if sound_enabled: hit_sound.play()
                reset_game()
                return

def on_mouse_down(pos):
    pass
