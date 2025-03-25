import pygame as pg
import pytmx.util_pygame

DEBUG = False

WHITE = pg.Color(255,255,255)
BLACK = pg.Color(0,0,0)
GRAY = pg.Color(128,128,128)
RED = pg.Color(255,0,0)
ORANGE = pg.Color(255, 128, 0)
YELLOW = pg.Color(255,255,0)
GREEN = pg.Color(0,255,0)
BLUE = pg.Color(0,0,255)

COLORS = {
    "background": WHITE
}

CALLOUTS = {
    "bank": [
        "Bank Shot!",
        "Bounce!",
    ],
    "combo": [
        "Combo!",
        "Double kill!",
        "Multishot!"
    ]
}

WIDTH = 800
HEIGHT = 512

TILE_W = 16
TILE_H = 16
CHARACTER_SCALE = 2/3

FPS = 60

SPEED = 8
BULLET_SPEED = 12
BULLET_BOUNCES = 3

ZOMBIE_SPEED = 2

CAMERA_LOCK_DIST = 70
CAMERA_FOLLOW_RATE = 0.07
CAMERA_FOLLOW_RATE_STOPPED = 0.2


from Layout import Layout
LEVELS = []
for i in range(3):
    LEVELS.append(Layout(f"tiles/levels/{i}.tmx"))
TILEMAP = LEVELS[0]

TILEMAP_LOCATIONS = {
    "Wall": (1, 9),
    "Goal": (9, 9)
}