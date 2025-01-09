import pygame as pg
from settings import *
import math, random
from sprites import SpriteSheet, Entity


screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)

clock = pg.time.Clock()

import sys
from pathlib import Path
dir = Path(sys.argv[0]).parent

characters = SpriteSheet(Path(dir, "images/characters.png"), (54, 44))
tilesheet = SpriteSheet(Path(dir, "images/tilesheet.png"), (16,16), (1,1))

player = Entity(characters.get_sprite((0,1)), [WIDTH/2, HEIGHT/2])

layout = []
for y, row in enumerate(LAYOUT):
    y *= TILE_H
    for x, char in enumerate(row):
        x *= TILE_W
        sprite_pos = LAYOUT_KEY[char]
        if type(sprite_pos) is list:
            sprite_pos = random.choice(sprite_pos)
        layout.append(Entity(tilesheet.get_sprite(sprite_pos), (x, y), (TILE_W,TILE_H)))

# Game loop
playing = True
while playing:
    # Event loop
    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
            playing = False
        elif event.type == pg.WINDOWSIZECHANGED:
            WIDTH = event.x
            HEIGHT = event.y
    
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


    # Update

    # Rendering
    screen.fill(COLORS["background"])

    for tile in layout:
        tile.render(screen)

    player.render(screen)

    pg.display.flip()

    # Delay
    clock.tick(FPS)


pg.quit()