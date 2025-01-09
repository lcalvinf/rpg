import pygame as pg
from pathlib import Path
import random

from settings import *
from sprites import SpriteSheet, Entity

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()

        self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
        self.clock = pg.time.Clock()

        # self.playing indicates if the update-display loop is running
        # setting it to False will end the current loop and transition to the next game screen (game over, start, etc.)
        self.playing = False
        # self.running indicates if the game is running at all
        # setting it to False will close the game entirely
        self.running = True
        import sys
        from pathlib import Path
        dir = Path(sys.argv[0]).parent
        self.spritesheets = {
            "characters": SpriteSheet(Path(dir, "images/characters.png"), (54, 44)),
            "tilesheet": SpriteSheet(Path(dir, "images/tilesheet.png"), (16,16), (1,1))
        }

        self.player = Entity(self.spritesheets["characters"].get_sprite((0,1)), [WIDTH/2, HEIGHT/2])
        self.layout = self.load_tiles()
    
    def load_tiles(self) -> list[Entity]:
        layout = []
        for y, row in enumerate(LAYOUT):
            y *= TILE_H
            for x, char in enumerate(row):
                x *= TILE_W
                sprite_pos = LAYOUT_KEY[char]
                if type(sprite_pos) is list:
                    sprite_pos = random.choice(sprite_pos)
                layout.append(Entity(self.spritesheets["tilesheet"].get_sprite(sprite_pos), (x, y), (TILE_W,TILE_H)))
        return layout
    
    def new(self):
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
        player = self.player
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            player.dir = 90
            player.pos[1] -= 10
        elif keys[pg.K_DOWN]:
            player.dir = 270 
            player.pos[1] += 10
        elif keys[pg.K_LEFT]:
            player.dir = 180
            player.pos[0] -= 10
        elif keys[pg.K_RIGHT]:
            player.dir = 0
            player.pos[0] += 10

    def draw(self):
        self.screen.fill(COLORS["background"])

        for tile in self.layout:
            tile.render(self.screen)

        self.player.render(self.screen)

        pg.display.flip()
    
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
                