import pygame as pg
import random
import math

from settings import *
from utils import *
from sprites import SpriteSheet, Entity, Player

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()

        self.final_screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
        self.screen = pg.Surface((TILE_W*len(LAYOUT[0] ), TILE_H*len(LAYOUT)), self.final_screen.get_flags())
        self.clock = pg.time.Clock()

        # self.playing indicates if the update-display loop is running
        # setting it to False will end the current loop and transition to the next game screen (game over, start, etc.)
        self.playing = False
        # self.running indicates if the game is running at all
        # setting it to False will close the game entirely
        self.running = True

        self.spritesheets: dict[str, SpriteSheet] = {}
        self.load_spritesheet("characters", (54, 44))
        self.load_spritesheet("tilesheet", (16, 16), (1,1))

        self.layout = []
        self.player = None

        self.camera = [WIDTH/2, HEIGHT/2]
    
    def load_spritesheet(self, name:str, *args):
        import sys
        from pathlib import Path
        dir = Path(sys.argv[0]).parent
        self.spritesheets[name] = SpriteSheet(Path(dir, f"images/{name}.png"), *args)

    
    def load_layout(self, layout_raw) -> list[Entity]:
        layout = []
        for y, row in enumerate(layout_raw):
            y *= TILE_H
            for x, char in enumerate(row):
                x *= TILE_W
                if LAYOUT_KEY["player"] == char:
                    self.player.pos = [x,y]
                    char = " "
                sprite_pos = LAYOUT_KEY[char]
                if type(sprite_pos) is list:
                    sprite_pos = random.choice(sprite_pos)
                rotation = 0
                if len(sprite_pos) > 2:
                    rotation = sprite_pos[2]
                    sprite_pos = [sprite_pos[0], sprite_pos[1]]
                layout.append(Entity(pg.transform.rotate(self.spritesheets["tilesheet"].get_sprite(sprite_pos),rotation), (x, y), (TILE_W,TILE_H)))
        return layout
    
    # Start a new game
    def new(self):
        self.player = Player(self.spritesheets["characters"].get_sprite((0,1)), [WIDTH/2, HEIGHT/2])
        self.layout = self.load_layout(LAYOUT)
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

    def update(self):
        self.player.update()
        if square_dist(self.camera, self.player.pos) <= CAMERA_LOCK_DIST**2:
            self.camera = [*self.player.pos]
        else:
            dpos = sub_vectors(self.player.pos, self.camera)
            dpos = scale_vector(dpos, CAMERA_FOLLOW_RATE)
            self.camera = add_vectors(self.camera, dpos)

    def draw(self):
        self.screen.fill(COLORS["background"])

        for tile in self.layout:
            tile.render(self.screen)

        self.player.render(self.screen)

        self.final_screen.fill(COLORS["background"])
        self.final_screen.blit(self.screen, sub_vectors(self.final_screen.get_rect().center, self.camera))

        pg.display.flip()
    
    # Show the start screen
    def start(self):
        pass

    def game_over(self):
        pass

    def quit(self):
        self.playing = False
        self.running = False
        pg.quit()

    def run(self):
        self.playing = True
        while self.playing:
            self.handle_events()
            self.update()
            self.draw()

            # Delay
            self.clock.tick(FPS)

        pg.quit()
                