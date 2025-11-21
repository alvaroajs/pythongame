import random
import math
from pygame import Rect

WIDTH = 1024
HEIGHT = 720
TITLE = "Survival Game: Final Version"

COLOR_BG_MENU = (20, 20, 20)
COLOR_BG_GAME = (28, 28, 32)
COLOR_BG_GAMEOVER = (50, 10, 10)
COLOR_BTN_NORMAL = (60, 60, 60)
COLOR_BTN_HOVER = (100, 100, 100)
COLOR_TEXT = (255, 255, 255)

STATE_MENU = "MENU"
STATE_GAME = "GAME"
STATE_GAMEOVER = "GAMEOVER"

game_state = STATE_MENU
sound_enabled = True
score = 0
score_timer = 0 


tactic_state = 0 
tactic_timer = 0
TACTIC_INTERVAL = 300

class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = Rect(x, y, w, h)
        self.hovered = False

    def draw(self, screen):
        color = COLOR_BTN_HOVER if self.hovered else COLOR_BTN_NORMAL
        screen.draw.filled_rect(self.rect, color)
        screen.draw.text(self.text, center=self.rect.center, fontsize=30, color=COLOR_TEXT)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class GameActor(Actor):
    def __init__(self, img_idle, img_walk, x, y):
        super().__init__(img_idle, pos=(x, y))
        self.img_idle = img_idle
        self.img_walk = img_walk
        self.frame_timer = 0
        self.is_moving = False

    def animate(self):
        self.frame_timer += 1
        if self.frame_timer > 10:
            self.frame_timer = 0
            if self.is_moving:
                self.image = self.img_walk if self.image == self.img_idle else self.img_idle
            else:
                self.image = self.img_idle

class Hero(GameActor):
    def __init__(self):
        super().__init__('hero_idle', 'hero_walk', WIDTH // 2, HEIGHT // 2)
        self.speed = 3

    def update(self):
        self.is_moving = False
        if keyboard.left and self.left > 0:
            self.x -= self.speed; self.is_moving = True
        if keyboard.right and self.right < WIDTH:
            self.x += self.speed; self.is_moving = True
        if keyboard.up and self.top > 0:
            self.y -= self.speed; self.is_moving = True
        if keyboard.down and self.bottom < HEIGHT:
            self.y += self.speed; self.is_moving = True
        self.animate()

    def reset(self):
        self.pos = (WIDTH // 2, HEIGHT // 2)


class Enemy(GameActor):
    def __init__(self, x, y, index):
        super().__init__('enemy_idle', 'enemy_walk', x, y)
        self.index = index 
        self.current_behavior = "zigzag" 
        self.speed_chase = 1.4
        self.speed_zigzag = 1.0
        self.zz_dx = random.choice([-1, 1])
        self.zz_dy = random.choice([-1, 1])

    def update_ai(self, target):
        self.is_moving = True
        
        if self.current_behavior == "chaser":
            dx = target.x - self.x
            dy = target.y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                self.x += (dx / dist) * self.speed_chase
                self.y += (dy / dist) * self.speed_chase
                
        elif self.current_behavior == "zigzag":
            self.x += self.zz_dx * self.speed_zigzag
            self.y += self.zz_dy * self.speed_zigzag
            
            if self.left < 0:
                self.x = 0; self.zz_dx = 1
            if self.right > WIDTH:
                self.x = WIDTH; self.zz_dx = -1
            if self.top < 0:
                self.y = 0; self.zz_dy = 1
            if self.bottom > HEIGHT:
                self.y = HEIGHT; self.zz_dy = -1

        self.animate()

hero = Hero()
enemies = []


BTN_W = 200
BTN_H = 50
BTN_X = (WIDTH - BTN_W) // 2

btn_start = Button("Começar", BTN_X, 250, BTN_W, BTN_H)
btn_sound = Button("Som: Ligado", BTN_X, 330, BTN_W, BTN_H)
btn_exit = Button("Sair", BTN_X, 410, BTN_W, BTN_H)

RESTART_W = 300
RESTART_X = (WIDTH - RESTART_W) // 2

btn_restart = Button("Voltar ao Menu", RESTART_X, 400, RESTART_W, 50)

def spawn_enemies():
    new_enemies = []
    for i in range(5):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        while abs(x - hero.x) < 150 and abs(y - hero.y) < 150:
            x = random.randint(50, WIDTH - 50)
            y = random.randint(50, HEIGHT - 50)
        new_enemies.append(Enemy(x, y, i))
    apply_tactics(new_enemies)
    return new_enemies

def apply_tactics(enemy_list):
    for e in enemy_list:
        if tactic_state == 0:
            if e.index < 2: e.current_behavior = "zigzag"
            else: e.current_behavior = "chaser"
        else:
            if e.index < 2: e.current_behavior = "chaser"
            else: e.current_behavior = "zigzag"


def play_sound(snd_name):
    if sound_enabled:
        try:
            if snd_name == 'click': sounds.click.play()
            elif snd_name == 'hit': sounds.hit.play()
        except: pass


def manage_music():
    """
    Toca música APENAS se estiver no jogo (STATE_GAME) e som ligado.
    Para a música se for ao Menu ou Game Over.
    """
    if sound_enabled and game_state == STATE_GAME:
        if not music.is_playing('theme'):
            try:
                music.play('theme')
                music.set_volume(0.3)
            except: pass
    else:
        
        if music.is_playing('theme'):
            music.stop()


def draw():
    screen.clear()
    
    if game_state == STATE_MENU:
        screen.fill(COLOR_BG_MENU)
        screen.draw.text("SOBREVIVA", center=(WIDTH // 2, 150), fontsize=60, color="white")
        btn_start.draw(screen)
        btn_sound.draw(screen)
        btn_exit.draw(screen)
        
    elif game_state == STATE_GAME:
        screen.fill(COLOR_BG_GAME)
        hero.draw()
        for e in enemies:
            e.draw()
        screen.draw.text(f"Pontos: {score}", (20, 20), fontsize=30, color="yellow")

    elif game_state == STATE_GAMEOVER:
        screen.fill(COLOR_BG_GAMEOVER)
        screen.draw.text("GAME OVER", center=(WIDTH // 2, 200), fontsize=70, color="red")
        screen.draw.text(f"Sua Pontuação Final: {score}", center=(WIDTH // 2, 300), fontsize=40, color="white")
        btn_restart.draw(screen)

def update():
    global game_state, score, score_timer, enemies
    global tactic_timer, tactic_state

    manage_music()

    if game_state == STATE_MENU:
        pass

    elif game_state == STATE_GAME:
        hero.update()
        
        if len(enemies) == 0:
            enemies = spawn_enemies()
            tactic_timer = 0
            tactic_state = 0

        tactic_timer += 1
        if tactic_timer >= TACTIC_INTERVAL:
            tactic_timer = 0
            tactic_state = 1 if tactic_state == 0 else 0
            apply_tactics(enemies)

        for e in enemies:
            e.update_ai(hero)
            if hero.colliderect(e):
                play_sound('hit')
                game_state = STATE_GAMEOVER

        score_timer += 1
        if score_timer >= 6:
            score += 1
            score_timer = 0

    elif game_state == STATE_GAMEOVER:
        pass

def on_mouse_move(pos):
    if game_state == STATE_MENU:
        btn_start.update(pos)
        btn_sound.update(pos)
        btn_exit.update(pos)
    elif game_state == STATE_GAMEOVER:
        btn_restart.update(pos)

def on_mouse_down(pos):
    global game_state, sound_enabled, enemies, score, score_timer
    
    if game_state == STATE_MENU:
        if btn_start.is_clicked(pos):
            play_sound('click')
            hero.reset()
            enemies = []
            score = 0
            score_timer = 0
            game_state = STATE_GAME
        if btn_sound.is_clicked(pos):
            sound_enabled = not sound_enabled
            btn_sound.text = f"Som: {'Ligado' if sound_enabled else 'Desligado'}"
            play_sound('click')
        if btn_exit.is_clicked(pos):
            quit()

    elif game_state == STATE_GAMEOVER:
        if btn_restart.is_clicked(pos):
            play_sound('click')
            
            hero.reset()
            enemies = []
            score = 0
            score_timer = 0
            game_state = STATE_MENU