import pygame as pg
from pygame import *
from pygame.sprite import *
import sys
from random import choice, random

vec = pg.math.Vector2


from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

#Initialise
pygame.init()

#Set colours
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)


#Screen settings       
FPS = 60
BGCOLOR = (40, 40, 40) #Dark Grey
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

#32 x 24
TILE_SIZE = 32
GRID_WIDTH = SCREEN_WIDTH / TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT / TILE_SIZE

global PLAYER_HEALTH
global BULLET_DAMAGE
global PLAYER_SPEED

#300 Pixels per second
PLAYER_SPEED = 300
PLAYER_ROTATION_SPEED = 250 #Degrees per second
PLAYER_HITBOX = pg.Rect(0, 0, 40, 40)
PLAYER_IMG = 'man.png'
PLAYER_HEALTH = 100

#Wall Settings
WALL_IMG = 'tileGreen_39.png'

#Gun Settings
BULLET_IMG = 'bullet.png'
BULLET_SPEED = 500
BULLET_LIFETIME = 1000
BULLET_RATE = 150
BULLET_DAMAGE = 10


#Enemy Settings
MOB_IMG = 'zombie.png'
MOB_SPEED = 150
MOB_HITBOX = pg.Rect(0, 0, 35, 35)
global MOB_HEALTH
global MOB_DAMAGE
#MOB_HEALTH = 100
#MOB_DAMAGE = 10
MOB_KNOCKBACK = 20

#Sounds
BG_MUSIC = 'background.mp3'
PLAYER_HIT_SOUNDS = ['pain/8.wav', 'pain/9.wav', 'pain/10.wav', 'pain/11.wav']
WEAPON_SOUNDS_GUN = ['sfx_weapon_singleshot2.wav']
ZOMBIE_DEATH_SOUNDS = ['splat-15.wav']

#Progression
power_ups = ['damage', 'movspeed', 'health']

#Health HUD
def draw_player_health(surface, x, y, percentage):
    if percentage < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20

    fill = percentage * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    filled_rect = pg.Rect(x, y, fill, BAR_HEIGHT)

    if percentage > 0.6:
        col = GREEN
    elif percentage > 0.3 and percentage <= 0.6:
        col = YELLOW
    else:
        col = RED

    pg.draw.rect(surface, col, filled_rect)
    pg.draw.rect(surface, (255, 255, 255), outline_rect, 2)

    
#Returns the collide rect from the collision between the hitbox of sprite one and the rect of sprite two
def collide_hit_rect(one, two):
    return one.hit_box.colliderect(two.rect)


#Checks wall collision
def collide_with_walls(sprite, group, axis):
    if axis == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            #If player's center is greater than walls center then im on right side of wall
            if hits[0].rect.centerx > sprite.hit_box.centerx:
                sprite.position.x = hits[0].rect.left - sprite.hit_box.width / 2
            if hits[0].rect.centerx < sprite.hit_box.centerx:
                sprite.position.x = hits[0].rect.right + sprite.hit_box.width / 2
            sprite.velocity.x = 0
            sprite.hit_box.centerx = sprite.position.x
    if axis == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_box.centery:
                sprite.position.y = hits[0].rect.top - sprite.hit_box.height / 2
            if hits[0].rect.centery < sprite.hit_box.centery:
                sprite.position.y = hits[0].rect.bottom + sprite.hit_box.height / 2
            sprite.velocity.y = 0
            sprite.hit_box.centery = sprite.position.y


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Covid-19 Fighter in the UK")
        self.clock = pg.time.Clock()
        self.level = 1
        self.load_Data(self.level)
        self.difficulty = "Easy"
        self.state = ""
        self.cursor_rect = pg.Rect(0, 0, 20, 20)
        self.power = "Damage"


    #Methods to draw text and align it
    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
            
        self.screen.blit(text_surface, text_rect)

        
    #Load initial data for levels
    def load_Data(self, level):
        resources = "Resources/"
        if level == 1:
            self.map = Map(resources + 'Maps/map.txt')
            self.wall_img = pg.image.load(resources + WALL_IMG).convert_alpha()
            self.wall_img = pygame.transform.scale(self.wall_img, (TILE_SIZE, TILE_SIZE))
        elif level == 2:
            self.map = Map(resources + 'Maps/map2.txt')
            self.wall_img = pg.image.load(resources + 'wall4.png').convert_alpha()
            self.wall_img = pygame.transform.scale(self.wall_img, (TILE_SIZE, TILE_SIZE))
        elif level == 3:
            self.map = Map(resources + 'Maps/map3.txt')
            self.wall_img = pg.image.load(resources + 'blockswalls_49.png').convert_alpha()
            self.wall_img = pygame.transform.scale(self.wall_img, (TILE_SIZE, TILE_SIZE))

        self.hud_font = resources + 'Fonts/Impacted2.0.ttf'
        self.title_font =  resources + 'Fonts/ZOMBIE.TTF'
        
        self.player_img = pg.image.load(resources + PLAYER_IMG).convert_alpha()
        self.player_img = pygame.transform.scale(self.player_img, (49, 43))
        

        self.mob_img = pg.image.load(resources + MOB_IMG).convert_alpha()

        self.bullet_img = pg.image.load(resources + BULLET_IMG).convert_alpha()
        self.bullet_img = pygame.transform.scale(self.bullet_img, (10, 10))

        self.flag_img = pg.image.load(resources + 'flag.png').convert_alpha()
        self.flag_img = pygame.transform.scale(self.flag_img, (TILE_SIZE*4, TILE_SIZE*2))

        #Load Sounds
        pg.mixer.music.load(resources + 'Music/' + BG_MUSIC) #Background Music

        self.weapon_sounds = {}
        self.weapon_sounds['gun'] = []
        for snd in WEAPON_SOUNDS_GUN:
            s = pg.mixer.Sound(resources + 'Music/' + snd)
            s.set_volume(0.3)
            self.weapon_sounds['gun'].append(s)

        self.player_hit_sounds = []
        for sound in PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(pg.mixer.Sound(resources + 'Music/' + sound))

        self.zombie_death_sounds = []
        for sd in ZOMBIE_DEATH_SOUNDS:
            d = pg.mixer.Sound(resources + 'Music/' + sd)
            d.set_volume(0.2)
            self.zombie_death_sounds.append(d)
            
            

    #Draws symbol next to options in menu
    def draw_cursor(self):
        self.draw_text("-", self.title_font, 75, (255, 255, 255),  self.cursor_rect.x,  self.cursor_rect.y, align="center")

    #Opening Screen
    def show_start_screen(self):
        self.menu_wait = True
        self.difficulty = "Easy"
        midx = SCREEN_WIDTH / 2
        midy = SCREEN_HEIGHT / 2
        
        easy = 350
        normal = 450
        hard = 550

        self.cursor_rect.midtop = (midx - 230, easy)

        #Event handling
        while self.menu_wait == True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.menu_wait = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pg.K_DOWN:
                        self.state = "DOWN"
                    if event.key == pygame.K_UP:
                        self.state = "UP"
                    if event.key == pygame.K_RETURN:
                        self.state = "START"

            self.check_input(midx)
            
            self.screen.fill((0, 0, 0))
            self.draw_text("Select Difficulty", self.title_font, 100, RED,
                       SCREEN_WIDTH / 2, 150, align="center")

            self.draw_text("Easy", self.title_font, 75, (255, 255, 255),
                       SCREEN_WIDTH / 2, easy, align="center")

            self.draw_text("Normal", self.title_font, 75, (255, 255, 255),
                       SCREEN_WIDTH / 2, normal, align="center")

            self.draw_text("Hard", self.title_font, 75, (255, 255, 255),
                       SCREEN_WIDTH / 2, hard, align="center")

            self.draw_cursor()

            pg.display.flip()


    #Power up screen
    def progression_screen(self):
        self.menu_wait = True
        self.state = ""
        self.power = "Damage"
        
        midx = SCREEN_WIDTH / 2
        midy = SCREEN_HEIGHT / 2
        
        easy = 350
        normal = 450
        hard = 550

        self.cursor_rect.midtop = (midx - 260, easy)
        #Event checking
        while self.menu_wait == True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.menu_wait = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pg.K_DOWN:
                        self.state = "DOWN"
                    if event.key == pygame.K_UP:
                        self.state = "UP"
                    if event.key == pygame.K_RETURN:
                        self.state = "START"

            self.check_input_prog(midx)
            
            self.screen.fill((0, 0, 0))
            self.draw_text("Select A Power Up", self.title_font, 75, RED,
                       SCREEN_WIDTH / 2, 150, align="center")

            self.draw_text("Gain 10 Bullet Damage", self.title_font, 40, (255, 255, 255),
                       SCREEN_WIDTH / 2, easy, align="center")

            self.draw_text("Gain 50 Health", self.title_font, 40, (255, 255, 255),
                       SCREEN_WIDTH / 2, normal, align="center")

            self.draw_text("Gain 30 Movement Speed", self.title_font, 40, (255, 255, 255),
                       SCREEN_WIDTH / 2, hard, align="center")

            self.draw_cursor()

            pg.display.flip()

    #Move symbol in menu to match current option
    def move_cursor(self, x):
        
        if self.state == "DOWN":
            self.state = ""
            if self.difficulty == "Easy":
                self.cursor_rect.midtop = (x - 260, 450)
                self.difficulty = "Normal"
            elif self.difficulty == "Normal":
                self.cursor_rect.midtop = (x - 260, 550)
                self.difficulty = "Hard"
            elif self.difficulty == "Hard":
                self.cursor_rect.midtop = (x - 260, 350)
                self.difficulty = "Easy"

        if self.state == "UP":
            self.state = ""
            if self.difficulty == "Easy":
                self.cursor_rect.midtop = (x - 260, 550)
                self.difficulty = "Hard"
            elif self.difficulty == "Normal":
                self.cursor_rect.midtop = (x - 260, 350)
                self.difficulty = "Easy"
            elif self.difficulty == "Hard":
                self.cursor_rect.midtop = (x - 260, 450)
                self.difficulty = "Normal"

    #Checks the user input for main menu
    def check_input(self, x):
        global MOB_HEALTH
        global MOB_DAMAGE
        self.move_cursor(x)
        if self.state == "START":
            self.state = ""
            if self.difficulty == "Easy":
                self.playing = True
                MOB_HEALTH = 50
                MOB_DAMAGE = 5
            elif self.difficulty == "Normal":
                MOB_HEALTH = 100
                MOB_DAMAGE = 10
                self.playing = True
            elif self.difficulty == "Hard":
                MOB_HEALTH = 180
                MOB_DAMAGE = 20
                self.playing = True

            self.menu_wait = False


    #Positions cursor on menu
    def move_cursor_prog(self, x):
        if self.state == "DOWN":
            self.state = ""
            if self.power == "Damage":
                self.cursor_rect.midtop = (x - 260, 450)
                self.power = "Health"
            elif self.power == "Health":
                self.cursor_rect.midtop = (x - 260, 550)
                self.power = "Speed"
            elif self.power == "Speed":
                self.cursor_rect.midtop = (x - 260, 350)
                self.power = "Damage"

        if self.state == "UP":
            self.state = ""
            if self.power == "Damage":
                self.cursor_rect.midtop = (x - 260, 550)
                self.power = "Speed"
            elif self.power == "Health":
                self.cursor_rect.midtop = (x - 260, 350)
                self.power = "Damage"
            elif self.power == "Speed":
                self.cursor_rect.midtop = (x - 260, 450)
                self.power = "Health"

    #Checks the user input for power up menu
    def check_input_prog(self, x):
        global PLAYER_HEALTH
        global BULLET_DAMAGE
        global PLAYER_SPEED
        self.move_cursor_prog(x)
        if self.state == "START":
            self.state = ""
            if self.power == "Health":
                PLAYER_HEALTH += 50
            elif self.power == "Damage":
                BULLET_DAMAGE += 10
            elif self.power == "Speed":
                PLAYER_SPEED += 30

            self.menu_wait = False

    def new_run(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()


        #Creating Walls and mobs
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row, 1)
                if tile == '2':
                    Wall(self, col, row, 2)
                if tile == 'M':
                    Mob(self, col, row)
                if tile == 'P':
                    self.player = Player(self, col, row)

        self.camera = Camera(self.map.width, self.map.height)
                    

    def game_loop(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        pg.mixer.music.play(loops=-1) #Background Music
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()


    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player) #Tracks from sprite given, could be player, could be enemy, could be bullet

        #Game Over or next level
        if len(self.mobs) == 0:
            for sprite in self.all_sprites:
                    sprite.kill()
                    
            self.level += 1
            if self.level < 4:
                self.progression_screen()
                self.load_Data(self.level)
                self.new_run()
                self.game_loop()
            else:
                self.playing = False
            
            

        #Mob Collision against Player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            if random() < 0.7:
                choice(self.player_hit_sounds).play()
            self.player.health -= MOB_DAMAGE
            hit.velocity = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False

        if hits:
            self.player.position += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rotation)
        #Bullet collision with with mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            hit.health -= BULLET_DAMAGE
            hit.velocity = vec(0, 0)

    #Background grid to check for rect boxes and image sizes
    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pg.draw.line(self.screen, (100, 100, 100), (x, 0), (x, SCREEN_HEIGHT))
            
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pg.draw.line(self.screen, (100, 100, 100), (0, y), (SCREEN_WIDTH, y))

    def draw(self):
        #Checks fps
        #pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.fill(BGCOLOR)
        #self.draw_grid()
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        #self.all_sprites.draw(self.screen)

        #Player Health and Score
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        self.draw_text('Zombies: {}'.format(len(self.mobs)), self.hud_font, 30, (255, 255, 255), SCREEN_WIDTH - 10, 10, align="ne")

        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()


    def show_go_screen(self):
        self.screen.fill((0,0,0))
        self.draw_text("GAME OVER", self.title_font, 100, RED,
                       SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, align="center")
        self.draw_text("Press a key to start", self.title_font, 75, (255, 255, 255),
                       SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4, align="center")
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False

class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        self.tile_width = len(self.data[0])
        self.tile_height = len(self.data)
        #Pixel width of map
        self.width = self.tile_width * TILE_SIZE
        self.height = self.tile_height * TILE_SIZE

#Handles camera movement
class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        #Need to move offset to opposite of target
        x = -target.rect.centerx + int(SCREEN_WIDTH /2)
        y = -target.rect.centery + int(SCREEN_HEIGHT /2)

        #Limit scrolling to map size
        x = min(0, x) #Stop scrolling once reached left side of map
        y = min(0, y) #Stop scrolling once reached top side of map
        x = max(-(self.width - SCREEN_WIDTH), x) #right
        y = max(-(self.height - SCREEN_HEIGHT), y) #bot
        self.camera = pg.Rect(x, y, self.width, self.height)

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.hit_box = PLAYER_HITBOX
        self.hit_box.center = self.rect.center
        self.velocity = vec(0, 0)
        self.position = vec(x, y) * TILE_SIZE
        self.rotation = 0 #Positive x-axis
        self.last_shot = 0
        self.health = PLAYER_HEALTH

    def get_key_press(self):
        self.rotation_speed = 0
        self.velocity = vec(0, 0)

        keys = pg.key.get_pressed()
        
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rotation_speed = PLAYER_ROTATION_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rotation_speed = -PLAYER_ROTATION_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.velocity = vec(PLAYER_SPEED, 0).rotate(-self.rotation)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.velocity = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rotation)
        if keys[pg.K_SPACE]:
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                direction = vec(1, 0).rotate(-self.rotation)
                Bullet(self.game, self.position, direction)
                self.game.weapon_sounds['gun'][0].play()


    def update(self):
        self.get_key_press()
        #Frame Independant Movement

        #Sets rotation
        self.rotation = (self.rotation + self.rotation_speed * self.game.dt) % 360
        #Rotates Player to match rotation
        self.image = pg.transform.rotate(self.game.player_img, self.rotation)
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        #Moves Player in the direct and velocity given
        self.position += self.velocity * self.game.dt
        #Sets x and y rects while also checking for collision among the walls
        self.hit_box.centerx = self.position.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_box.centery = self.position.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_box.center


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img
        self.rect = self.image.get_rect()
        self.hit_box = MOB_HITBOX.copy()
        self.hit_box.center = self.rect.center
        self.position = vec(x, y) * TILE_SIZE
        self.velocity = vec(0, 0)
        #Make it look like its running
        self.acc = vec(0, 0)
        self.rect.center = self.position
        self.rotation = 0
        self.health = MOB_HEALTH

    def update(self):
        self.rotation = (self.game.player.position - self.position).angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.game.mob_img, self.rotation)
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        self.acc = vec(MOB_SPEED, 0).rotate(-self.rotation)
        self.acc += self.velocity * -1 #Add resistance to mob acceleration
        self.velocity += self.acc * self.game.dt
        self.position += self.velocity * self.game.dt + 0.5 * self.acc * self.game.dt ** 2 #Equations of motion
        self.hit_box.centerx = self.position.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_box.centery = self.position.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_box.center
        if self.health <= 0:
            choice(self.game.zombie_death_sounds).play()
            self.kill()

    #Display mob health
    def draw_health(self):
        if self.health >60:
            col = GREEN
        elif self.health > 30 and self.health <=60:
            col = YELLOW
        else:
            col = RED

        width = int(self.rect.width * self.health/ MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)

        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)



class Bullet(pg.sprite.Sprite):
    def __init__(self, game, position, direction):
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_img
        self.rect = self.image.get_rect()
        self.position = vec(position) #Copies player position so that it doesn't affect the player
        self.rect.center = position
        self.velocity = direction * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks() #Find how long it lasts

    def update(self):
        self.position += self.velocity * self.game.dt
        self.rect.center = self.position
        #If it lasts longer than a second, it disappears.
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y, w):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        if w == 1:
            self.image = game.wall_img
        else:
            self.image = game.flag_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

def main():
    g = Game()
    g.show_start_screen()
    while True:
        g.new_run()
        g.game_loop()
        g.show_go_screen()


if __name__ == "__main__":
    main()
