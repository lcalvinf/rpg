import pygame as pg
from settings import *


screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)

clock = pg.time.Clock()


# Game loop
playing = True
while playing:
    # Event loop
    for event in pg.event.get():
        if event.type == pg.QUIT:
            playing = False
        elif event.type == pg.WINDOWSIZECHANGED:
            WIDTH = event.x
            HEIGHT = event.y
    # Update

    # Rendering
    screen.fill(COLORS["background"])

    pg.display.flip()

    # Delay
    clock.tick(FPS)


pg.quit()