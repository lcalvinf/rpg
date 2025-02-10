import pygame as pg

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

TILE_W = 32
TILE_H = 32

FPS = 60

SPEED = 8
BULLET_SPEED = 12

ZOMBIE_SPEED = 2

CAMERA_LOCK_DIST = 70
CAMERA_FOLLOW_RATE = 0.07
CAMERA_FOLLOW_RATE_STOPPED = 0.2

LAYOUT = [
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@HHHHHHHHHHHHHHHHHHH@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@***@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "---------H-------------   -------H---------------",
    "         H              P        H               ",
    "_________H_____________   _______H_______________",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@HHHHHHHHHHHHHHHHHHH@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@***@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@***@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@[ ]@@@@@@@@@@@@@@@@@@@@@@@",
]

FULL_WIDTH = TILE_W*len(LAYOUT[0])
FULL_HEIGHT = TILE_H*len(LAYOUT)

from sprites import Wall
LAYOUT_KEY = {
    "#": (0,0),
    "@": [(0,0)]*8+[(1,0)]*4+[(2,0),(2,0,90)],
    "*": (2,0),
    " ": [(1,2)]*10+[(3,3),(4,3),(5,3),(6,3)],

    "H": (1,9),

    ".": (1,2),
    "[": (0,2),
    "]": (2,2),
    "-": (1,1),
    "_": (1,3),
    "{": (0,1),
    "}": (2, 1),
    "+": (0,3),
    "%": (2,3),

    "^": (3,0),
    "=": (3,1),
    "~": (4,0),
    "|": (4,1),

    "player": "P",
    "zombie": "Z",
    "special": {
        "H": Wall
    }
}