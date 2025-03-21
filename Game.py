import pygame as pg
import random
import math

from settings import *
from utils import *
from sprites import SpriteSheet, Goal, Player, Zombie, Wall, TextParticle
from Camera import Camera

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()

        self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
        self.clock = pg.time.Clock()

        self.font = pg.font.SysFont("sans-serif", 50)
        self.smallfont = pg.font.SysFont("sans-serif", 30)

        # self.playing indicates if the update-display loop is running
        # setting it to False will end the current loop and transition to the next game screen (game over, start, etc.)
        self.playing = False
        # self.running indicates if the game is running at all
        # setting it to False will close the game entirely
        self.running = True
        self.level = 0

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

        self.camera = Camera(WIDTH,HEIGHT)
    
    def load_spritesheet(self, name:str, *args):
        import sys
        from pathlib import Path
        dir = Path(sys.argv[0]).parent
        self.spritesheets[name] = SpriteSheet(Path(dir, f"images/{name}.png"), *args)

    
    def load_layout(self):
        TILEMAP.load()
        FULL_WIDTH = TILEMAP.full_width
        FULL_HEIGHT = TILEMAP.full_height

        for x in range(TILEMAP.width):
            x *= TILE_W
            Wall(self.spritesheets["tilesheet"].get_sprite(TILEMAP_LOCATIONS["Wall"]), (x, -TILE_H), (TILE_W,TILE_H)).add(self.all_sprites,self.layout,self.walls)
            Wall(self.spritesheets["tilesheet"].get_sprite(TILEMAP_LOCATIONS["Wall"]), (x,FULL_HEIGHT), (TILE_W,TILE_H)).add(self.all_sprites,self.layout,self.walls)
        for y in range(TILEMAP.height):
            y *= TILE_H
            Wall(self.spritesheets["tilesheet"].get_sprite(TILEMAP_LOCATIONS["Wall"]), (-TILE_W, y), (TILE_W,TILE_H)).add(self.all_sprites,self.layout,self.walls)
            Wall(self.spritesheets["tilesheet"].get_sprite(TILEMAP_LOCATIONS["Wall"]), (FULL_WIDTH, y), (TILE_W,TILE_H)).add(self.all_sprites,self.layout,self.walls)

        for tile in TILEMAP.tiles():
            if(type(tile) is tuple):
                tile_type, x, y = tile
                if tile_type == "player":
                    self.player.pos = (x, y)
                elif tile_type == "goal":
                    Goal(self.spritesheets["tilesheet"].get_sprite(TILEMAP_LOCATIONS["Goal"]), (x, y)).add(self.all_sprites, self.layout, self.walls)
                continue
            tile.add(self.all_sprites, self.layout)
            if type(tile) is Wall:
                tile.add(self.walls)
        return
    
    def next_level(self):
        global TILEMAP
        if self.level >= len(LEVELS)-1:
            return
        self.level += 1
        TILEMAP = LEVELS[self.level]
        self.new()
    
    def spawn_zombie(self):
        # This should make it stabilize at around 9 Zombies
        # and ensures there is always at least 1 Zombie
        for _ in range(8):
            if random.random() <= 1/(len(self.enemies)+1):
                pos = [random.randint(0,TILEMAP.full_width), random.randint(0,TILEMAP.full_height)]
                while not self.camera.is_off_screen(pos):
                    pos = [random.randint(0,TILEMAP.full_width), random.randint(0,TILEMAP.full_height)]
                zombie = Zombie(self.spritesheets["characters"].get_image(pg.Rect(424,0,37,43)), pos, (37*CHARACTER_SCALE,43*CHARACTER_SCALE))
                zombie.add(self.enemies, self.all_sprites)
                self.all_sprites.change_layer(zombie, 1)
                zombie.update(self)

    def spawn_text_particle(self, text, pos=None):
        if pos is None:
            pos = self.player.pos
        particle = TextParticle(self,text, pos)
        particle.add(self.particles,self.all_sprites)
        self.all_sprites.change_layer(particle,3)
        particle.update(self)
    
    # Start a new game
    def new(self):
        self.all_sprites.empty()
        self.enemies.empty()
        self.particles.empty()
        self.walls.empty()
        self.layout.empty()
        self.player = Player(self.spritesheets["characters"].get_sprite((0,1)), [WIDTH/2, HEIGHT/2], [54*CHARACTER_SCALE, 44*CHARACTER_SCALE])
        self.player.add(self.all_sprites)
        self.load_layout()
        for ent in self.enemies.sprites():
            self.all_sprites.change_layer(ent, 1)
        self.all_sprites.change_layer(self.player, 2)
        self.spawn_zombie()
        self.score = 0
        self.camera = Camera(WIDTH,HEIGHT)

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

        self.camera.update(self, self.player.pos)

    def draw(self):
        self.screen.fill(COLORS["background"])

        for tile in self.layout:
            tile.render(self)

        self.all_sprites.draw(self.screen)
        if DEBUG:
            debug_screen = pg.Surface((WIDTH*2,HEIGHT*2), self.screen.get_flags())
            debug_screen.blit(self.screen, self.camera.rect.topleft)
            target_pos = self.player.pos
            target_pos = add_vectors(self.player.pos, set_mag(self.player.old_vel, 0))
            pg.draw.circle(debug_screen, RED, target_pos, CAMERA_LOCK_DIST, 1)
            pg.draw.circle(debug_screen, RED, target_pos, CAMERA_LOCK_DIST*1.5, 1)
            pg.draw.circle(debug_screen, BLUE, self.camera.rect.center, 10, 1)
            pg.draw.line(debug_screen,RED,self.player.pos, add_vectors(self.player.pos,rotate_vector((20,0), self.player.dir)))
            self.screen.blit(debug_screen, scale_vector(self.camera.rect.topleft,-1))
        
        self.draw_HUD()

        pg.display.flip()
    def draw_HUD(self):
        screen = self.screen
        screen.blit(*draw_centered_text(self.font, str(self.score), BLACK, (WIDTH/2, 30)))
        if DEBUG:
            screen.blit(*draw_centered_text(self.smallfont, str(round(self.clock.get_fps(), 2)), GRAY, (100, HEIGHT-40)))
    
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
                    self.level = 0
            
            self.screen.fill(COLORS["background"])
            self.screen.blit(*draw_centered_text(self.font, str(self.score), BLACK, (WIDTH/2, 30)))
            self.screen.blit(*draw_centered_text(self.font, "GAME OVER", BLACK, (WIDTH/2, HEIGHT/2-30)))
            self.screen.blit(*draw_centered_text(self.smallfont, "Press any key to start over", BLACK, (WIDTH/2, HEIGHT/2+30)))
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

def draw_centered_text(font, text, color, center_pos):
    size = font.size(text)
    return (font.render(text, True, color), sub_vectors(center_pos, scale_vector(size, 1/2)))