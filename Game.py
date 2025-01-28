import pygame as pg
import random
import math

from settings import *
from utils import *
from sprites import SpriteSheet, Entity, Player, Zombie, Wall

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()

        self.final_screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
        self.screen = pg.Surface((TILE_W*len(LAYOUT[0] ), TILE_H*len(LAYOUT)), self.final_screen.get_flags())
        self.clock = pg.time.Clock()

        self.font = pg.font.SysFont("sans-serif", 50)
        self.smallfont = pg.font.SysFont("sans-serif", 30)

        # self.playing indicates if the update-display loop is running
        # setting it to False will end the current loop and transition to the next game screen (game over, start, etc.)
        self.playing = False
        # self.running indicates if the game is running at all
        # setting it to False will close the game entirely
        self.running = True

        self.spritesheets: dict[str, SpriteSheet] = {}
        self.load_spritesheet("characters", (54, 44))
        self.load_spritesheet("tilesheet", (16, 16), (1,1))

        self.layout = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.particles = pg.sprite.Group()
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.player = None
        self.score = 0

        self.camera = [WIDTH/2, HEIGHT/2]
    
    def load_spritesheet(self, name:str, *args):
        import sys
        from pathlib import Path
        dir = Path(sys.argv[0]).parent
        self.spritesheets[name] = SpriteSheet(Path(dir, f"images/{name}.png"), *args)

    
    def load_layout(self, layout_raw):
        for y, row in enumerate(layout_raw):
            y *= TILE_H
            for x, char in enumerate(row):
                x *= TILE_W
                if LAYOUT_KEY["player"] == char:
                    self.player.pos = [x,y]
                    char = " "
                elif LAYOUT_KEY["zombie"] == char:
                    Zombie(self.spritesheets["characters"].get_image(pg.Rect(424,0,37,43)),(x,y),(37,43)).add(self.enemies, self.all_sprites)
                    char = " "
                sprite_pos = LAYOUT_KEY[char]
                sprite_class = Entity
                if char in LAYOUT_KEY["special"]:
                    sprite_class = LAYOUT_KEY["special"][char]
                if type(sprite_pos) is list:
                    sprite_pos = random.choice(sprite_pos)
                rotation = 0
                if len(sprite_pos) > 2:
                    rotation = sprite_pos[2]
                    sprite_pos = [sprite_pos[0], sprite_pos[1]]
                entity = sprite_class(pg.transform.rotate(self.spritesheets["tilesheet"].get_sprite(sprite_pos),rotation), (x, y), (TILE_W,TILE_H))
                entity.add(self.all_sprites)
                if type(entity) is Wall:
                    entity.add(self.walls)
    
    def spawn_zombie(self):
        full_w = TILE_W*len(LAYOUT[0])
        full_h = TILE_H*len(LAYOUT)
        # This should make it stabilize at around 4 Zombies
        # and ensures there is always at least 1 Zombie
        for _ in range(4):
            if random.random() <= 1/(len(self.enemies)+1):
                pos = [full_w/2, full_h/2]
                while square_dist(pos, [full_w/2,full_h/2]) < (full_w/4)**2:
                    pos = [random.randint(0,full_w), random.randint(0,full_h)]
                zombie = Zombie(self.spritesheets["characters"].get_image(pg.Rect(424,0,37,43)), pos, (37,43))
                zombie.add(self.enemies, self.all_sprites)
                self.all_sprites.change_layer(zombie, 1)
    
    # Start a new game
    def new(self):
        self.all_sprites.empty()
        self.enemies.empty()
        self.particles.empty()
        self.walls.empty()
        self.layout.empty()
        self.player = Player(self.spritesheets["characters"].get_sprite((0,1)), [WIDTH/2, HEIGHT/2])
        self.player.add(self.all_sprites)
        self.load_layout(LAYOUT)
        for ent in self.enemies.sprites():
            self.all_sprites.change_layer(ent, 1)
        self.all_sprites.change_layer(self.player, 2)
        self.spawn_zombie()
        self.score = 0
        self.run()

    def handle_events(self):
        global WIDTH, HEIGHT
        # Event loop
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
                self.playing = False
                self.running = False
            elif event.type == pg.WINDOWSIZECHANGED:
                WIDTH = event.x
                HEIGHT = event.y
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.fire_bullet(self)

    def update(self):
        self.player.update(self)
        self.enemies.update(self)
        self.particles.update(self)

        if square_dist(self.camera, self.player.pos) > CAMERA_LOCK_DIST**2:
            dpos = sub_vectors(self.player.pos, self.camera)
            dpos = scale_vector(dpos, CAMERA_FOLLOW_RATE)
            self.camera = add_vectors(self.camera, dpos)

    def draw(self):
        self.screen.fill(COLORS["background"])

        self.all_sprites.draw(self.screen)

        self.final_screen.fill(COLORS["background"])
        self.final_screen.blit(self.screen, sub_vectors(self.final_screen.get_rect().center, self.camera))
        
        self.draw_HUD()

        pg.display.flip()
    def draw_HUD(self):
        screen = self.final_screen
        screen.blit(*draw_centered_text(self.font, str(self.score), BLACK, (WIDTH/2, 30)))
    
    # Show the start screen
    def start(self):
        pass

    def game_over(self):
        self.playing = self.running
        while self.playing:
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
                    self.playing = False
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    self.playing = False
            
            self.final_screen.fill(COLORS["background"])
            self.final_screen.blit(*draw_centered_text(self.font, str(self.score), BLACK, (WIDTH/2, 30)))
            self.final_screen.blit(*draw_centered_text(self.font, "GAME OVER", BLACK, (WIDTH/2, HEIGHT/2-30)))
            self.final_screen.blit(*draw_centered_text(self.smallfont, "Press any key to start over", BLACK, (WIDTH/2, HEIGHT/2+30)))
            pg.display.flip()
            self.clock.tick(FPS)

    def quit(self):
        self.playing = False
        self.running = False
        pg.quit()

    def run(self):
        self.playing = self.running
        while self.playing:
            self.handle_events()
            self.update()
            self.draw()

            # Delay
            self.clock.tick(FPS)
    
    def to_screen_coords(self,pos):
        return sub_vectors(pos, self.camera)
    def is_off_screen(self, pos):
        screen_pos = self.to_screen_coords(pos)
        return screen_pos[0] < -WIDTH/2 or screen_pos[0] > WIDTH/2 or screen_pos[1] < -HEIGHT/2 or screen_pos[1] > HEIGHT/2

def draw_centered_text(font, text, color, center_pos):
    size = font.size(text)
    return (font.render(text, True, color), sub_vectors(center_pos, scale_vector(size, 1/2)))